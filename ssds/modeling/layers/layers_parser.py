from ssds.modeling.layers.basic_layers import SepConvBNReLU, ConvBNReLUx2
from ssds.modeling.layers.rfb_layers import BasicRFB, BasicRFB_lite


def parse_feature_layer(layer, in_channels, depth):
    """ Parse the layers defined in the config files
    Args:
        layer:       The name of the layer
        in_channels: The input channel of the layer
        depth:       The output channel of the layer
    Return:
        list of operation
    """
    if layer == "SepConv:S":
        return [SepConvBNReLU(in_channels, depth, stride=2, expand_ratio=1)]
    elif layer == "SepConv":
        return [SepConvBNReLU(in_channels, depth, stride=1, expand_ratio=1)]
    elif layer == "Conv:S":
        return [ConvBNReLUx2(in_channels, depth, stride=2)]
    elif layer == "Conv":
        return [ConvBNReLUx2(in_channels, depth, stride=1)]
    elif layer == "RBF:S":
        return [BasicRFB(in_channels, depth, stride=2, scale=1.0, visual=2)]
    elif layer == "RBF":
        return [BasicRFB(in_channels, depth, stride=1, scale=1.0, visual=2)]
    elif isinstance(layer, int):
        # temp, need TODO improve
        return []
    else:
        raise AssertionError("Undefined layer: {}".format(layer))
