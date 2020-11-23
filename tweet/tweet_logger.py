
import logging
import torch
import numpy as np

from sklearn import metrics
from built.logger import LoggerBase
from built.registry import Registry


@Registry.register(category="hooks")
class TweetLogger(LoggerBase):
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

        if labels is not None and outputs is not None:
            labels = labels['sentiment_target']
            outputs = torch.sigmoid(outputs).cpu().detach().numpy().tolist()
            outputs = np.argmax(outputs, axis=1)

            writer['tensorboard'].add_pr_curve(
                f'pr_curve_{split}', labels, outputs, log_step)
            
            y = labels.numpy()
            pred = outputs
            fpr, tpr, thresholds = metrics.roc_curve(
                labels.numpy(), outputs, pos_label=2)
            auc = metrics.auc(fpr, tpr)
            
            writer['tensorboard'].add_scalar(
                f'auc_curve_{split}', auc, log_step)
            
