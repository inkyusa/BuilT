
import logging
import torch
import numpy as np

from sklearn import metrics
from built.logger import LoggerBase
from built.registry import Registry


@Registry.register(category="hooks")
class TweetIndexExtractionLogger(LoggerBase):
    def __call__(self, writer, split, outputs, labels, log_dict,
                 epoch, step=None, num_steps_in_epoch=None):

        if step is not None:
            assert num_steps_in_epoch is not None
            log_step = epoch * 10000 + (step / num_steps_in_epoch) * 10000
            log_step = int(log_step)
        else:
            log_step = epoch

        for key, value in log_dict.items():
            if self.use_tensorboard:
                writer['tensorboard'].add_scalar(
                    f'{split}/{key}', value, log_step)

        if self.use_wandb:
            log_dict.update({'epoch': epoch, 'mode': split})
            writer['wandb'].log(log_dict)

        # if labels is not None and outputs is not None:
        #     start_idx = labels['start_idx']
        #     end_idx = labels['end_idx']
        #     start_pred = torch.softmax(
        #                 outputs[0], dim=1).cpu().detach().numpy()
        #     end_pred = torch.softmax(
        #                 outputs[1], dim=1).cpu().detach().numpy()

        #     writer['tensorboard'].add_pr_curve(
        #         f'pr_curve_{split}_start_idx', start_idx, start_pred, log_step)

        #     writer['tensorboard'].add_pr_curve(
        #         f'pr_curve_{split}_end_idx', end_idx, end_pred, log_step)
            
            
