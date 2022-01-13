import dgl.nn as dglnn
import torch.nn as nn
import torch.nn.functional as F


class GCN(nn.Module):
    def __init__(self, in_feats, h_feats, num_classes):
        super(GCN, self).__init__()
        self.conv1 = dglnn.GraphConv(in_feats, h_feats)
        self.conv2 = dglnn.GraphConv(h_feats, num_classes)

    def forward(self, g, in_feat):
        h = self.conv1(g, in_feat)
        h = F.relu(h)
        h = self.conv2(g, h)
        return h


class RGCN(nn.Module):
    """
        Heterograph where we gather message from neighbors along all edge types.
        You can use the module dgl.nn.pytorch.HeteroGraphConv (also available in MXNet and Tensorflow) to perform
        message passing on all edge types,
        then combining different graph convolution modules for each edge type.

    :returns
        torch model with forward pass methods useful for fitting model in standard way
    """

    def __init__(self, in_feats, hid_feats, out_feats, rel_names):
        super().__init__()

        self.conv1 = dglnn.HeteroGraphConv(
            {rel: dglnn.GraphConv(in_feats, hid_feats) for rel in rel_names},
            aggregate="sum",
        )
        self.conv2 = dglnn.HeteroGraphConv(
            {rel: dglnn.GraphConv(hid_feats, out_feats) for rel in rel_names},
            aggregate="sum",
        )

    def forward(self, graph, inputs):
        # inputs are features of nodes
        h = self.conv1(graph, inputs)
        h = {k: F.relu(v) for k, v in h.items()}
        h = self.conv2(graph, h)
        return h