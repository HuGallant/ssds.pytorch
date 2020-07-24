import torch

import os
from collections import OrderedDict


def model_to_cpu(model_state):
    r""" make sure the model is load from cpu memory. In this case, the loaded model will not occupied the gpu memory.

    :meta private:
    """
    new_state = OrderedDict()
    for k, v in model_state.items():
        new_state[k] = v.cpu()
    return new_state


def save_checkpoints(model, output_dir, checkpoint_prefix, epochs):
    r"""Save the model parameter to a pth file.

    Args:
        model: the ssds model
        output_dir (str): the folder for model saving, usually defined by cfg.EXP_DIR
        checkpoint_prefix (str): the prefix for the checkpoint, usually is the combination of the ssd model and the dataset
        epochs (int): the epoch for the current training
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = checkpoint_prefix + "_epoch_{:d}".format(epochs) + ".pth"
    filename = os.path.join(output_dir, filename)
    torch.save(model_to_cpu(model.state_dict()), filename)
    with open(os.path.join(output_dir, "checkpoint_list.txt"), "a") as f:
        f.write("epoch {epoch:d}: {filename}\n".format(epoch=epochs, filename=filename))
    print("Wrote snapshot to: {:s}".format(filename))


def find_previous_checkpoint(output_dir):
    r"""Return the most recent checkpoint in the checkpoint_list.txt
    
    checkpoint_list.txt is usually saved at cfg.EXP_DIR

    Args:
        output_dir (str): the folder contains the previous checkpoints and checkpoint_list.txt
    """
    if not os.path.exists(os.path.join(output_dir, "checkpoint_list.txt")):
        return False
    with open(os.path.join(output_dir, "checkpoint_list.txt"), "r") as f:
        lineList = f.readlines()
    epoches, resume_checkpoints = [list() for _ in range(2)]
    for line in lineList:
        epoch = int(line[line.find("epoch ") + len("epoch ") : line.find(":")])
        checkpoint = line[line.find(":") + 2 : -1]
        epoches.append(epoch)
        resume_checkpoints.append(checkpoint)
    return epoches, resume_checkpoints


def resume_checkpoint(model, resume_checkpoint, resume_scope=""):
    r"""Resume the checkpoints to the given ssds model based on the resume_scope.

    The resume_scope is defined by cfg.TRAIN.RESUME_SCOPE.

    When:

    * cfg.TRAIN.RESUME_SCOPE = ""
        All the parameters in the resume_checkpoint are resumed to the model
    * cfg.TRAIN.RESUME_SCOPE = "a,b,c"
        Only the the parameters in the a, b and c are resumed to the model
    
    Args:
        model: the ssds model
        resume_checkpoint (str): the file address for the checkpoint which contains the resumed parameters
        resume_scope: the scope of the resumed parameters, defined at cfg.TRAIN.RESUME_SCOPE
    """
    if resume_checkpoint == "" or not os.path.isfile(resume_checkpoint):
        print(("=> no checkpoint found at '{}'".format(resume_checkpoint)))
        return False
    print(("=> loading checkpoint '{:s}'".format(resume_checkpoint)))
    checkpoint = torch.load(resume_checkpoint, map_location=torch.device("cpu"))
    if "state_dict" in checkpoint:
        checkpoint = checkpoint["state_dict"]

    # print("=> Weigths in the checkpoints:")
    # print([k for k, v in list(checkpoint.items())])

    # remove the module in the parrallel model
    if "module." in list(checkpoint.items())[0][0]:
        pretrained_dict = {
            ".".join(k.split(".")[1:]): v for k, v in list(checkpoint.items())
        }
        checkpoint = pretrained_dict

    # change the name of the weights which exists in other model
    # change_dict = {
    # }
    # for k, v in list(checkpoint.items()):
    #     for _k, _v in list(change_dict.items()):
    #         if _k in k:
    #             new_key = k.replace(_k, _v)
    #             checkpoint[new_key] = checkpoint.pop(k)

    # remove the output layers from the checkpoint
    # remove_list = {
    # }
    # for k in remove_list:
    #     checkpoint.pop(k+'.weight', None)
    #     checkpoint.pop(k+'.bias', None)

    # extract the weights based on the resume scope
    if resume_scope != "":
        pretrained_dict = {}
        for k, v in list(checkpoint.items()):
            for resume_key in resume_scope.split(","):
                if resume_key in k:
                    pretrained_dict[k] = v
                    break
        checkpoint = pretrained_dict

    pretrained_dict = {k: v for k, v in checkpoint.items() if k in model.state_dict()}
    # print("=> Resume weigths:")
    # print([k for k, v in list(pretrained_dict.items())])

    checkpoint = model.state_dict()
    unresume_dict = set(checkpoint) - set(pretrained_dict)
    if len(unresume_dict) != 0:
        print("=> UNResume weigths:")
        print(unresume_dict)

    checkpoint.update(pretrained_dict)

    model.load_state_dict(checkpoint)
    return model
