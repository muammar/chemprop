from argparse import Namespace

import torch.nn as nn

from jtnn import JTNN
from mpn import MPN


def build_model(args: Namespace) -> nn.Module:
    """
    Builds a message passing neural network including final linear layers and initializes parameters.

    :param args: Arguments.
    :return: An nn.Module containing the MPN encoder along with final linear layers with parameters initialized.
    """
    if args.dataset_type == 'regression_with_binning':
        output_size = args.num_bins * args.num_tasks
    else:
        output_size = args.num_tasks

    if args.jtnn:
        encoder = JTNN(args)
    else:
        encoder = MPN(args)
    
    if args.semiF_only:
        first_linear_dim = args.semiF_dim
    else:
        first_linear_dim = args.hidden_size * (1 + args.jtnn)
        if args.semiF_path:
            first_linear_dim += args.semiF_dim

    modules = [
        encoder,
        nn.Linear(first_linear_dim, args.hidden_size),
        nn.ReLU(),
        nn.Linear(args.hidden_size, output_size)
    ]
    if args.dataset_type == 'classification':
        modules.append(nn.Sigmoid())

    model = nn.Sequential(*modules)

    for param in model.parameters():
        if param.dim() == 1:
            nn.init.constant_(param, 0)
        else:
            nn.init.xavier_normal_(param)

    return model
