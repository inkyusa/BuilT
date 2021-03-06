
import torch.nn as nn
import torch.optim as optim
import yaml

from easydict import EasyDict as edict
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from .registry import Registry

from .forward_hook import DefaultPostForwardHook
from .metric import DefaultMetric
from .logger import DefaultLogger
from .models.mnist import Mnist

class Builder(object):
    def __init__(self):
        self.r = Registry()
        self.regist_defaults()

    def regist_defaults(self):
        self.r.add('loss', nn.NLLLoss)
        self.r.add('optimizer', optim.Adadelta)
        self.r.add('scheduler', optim.lr_scheduler.StepLR)
        self.r.add('dataset', datasets.MNIST)
        self.r.add('transform', transforms.ToTensor)
        self.r.add('transform', transforms.Normalize)
        self.r.add('hooks', DefaultPostForwardHook)
        self.r.add('hooks', DefaultMetric)
        self.r.add('hooks', DefaultLogger)
        self.r.add('model', Mnist)

    def build_model(self, config, **kwargs):
        return self.r.build_from_config('model', config.model, kwargs)

    def build_loss_fn(self, config, **kwargs):
        return self.r.build_from_config('loss', config.loss, kwargs)

    def build_optimizer(self, config, **kwargs):
        return self.r.build_from_config('optimizer', config.optimizer, kwargs)

    def build_scheduler(self, config, **kwargs):
        return self.r.build_from_config('scheduler', config.scheduler, kwargs)

    def build_post_forward_hook(self, config, **kwargs):
        return self.r.build_from_config('hooks', config.post_forward_hook, kwargs)

    def build_metric_fn(self, config, **kwargs):
        return self.r.build_from_config('hooks', config.metric_hook, kwargs)

    def build_logger_fn(self, config, **kwargs):
        return self.r.build_from_config('hooks', config.logger_hook, kwargs)

    def build_transforms(self, config, **kwargs):
        if config.transforms.name == 'Compose':
            transfms = []
            for t in config.transforms.params:
                transfms.append(self.r.build_from_config('transform', t))

            return transforms.Compose(transfms)
        else:
            return self.r.build_from_config('transform', config.transforms),

    def build_dataloaders(self, config, **kwargs):
        dataloaders = []
        for split_config in config.dataset.splits:
            dataset_config = edict({'name': config.dataset.name,
                                    'params': config.dataset.params})
            dataset_config.params.update(split_config)

            transform = self.build_transforms(config)

            dataset = self.r.build_from_config('dataset', config.dataset, default_args={'transform': transform})

            is_train = dataset_config.params.train
            if is_train:
                batch_size = config.train.batch_size
            else:
                batch_size = config.evaluation.batch_size
            dataloader = DataLoader(dataset,
                                    shuffle=is_train,
                                    batch_size=batch_size,
                                    drop_last=is_train,
                                    num_workers=config.transforms.num_preprocessor,
                                    pin_memory=True)

            dataloaders.append({'mode': is_train,'dataloader': dataloader})
        return dataloaders        
    
    def build_sweep(self, config):
        with open(r'config.wandb.sweep.yaml') as file:
            hyperparam = yaml.load(file, Loader=yaml.FullLoader)
            
    
