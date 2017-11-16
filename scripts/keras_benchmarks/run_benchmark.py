""" Main entry point for running benchmarks with different Keras backends."""

from models import mnist_mlp_benchmark
from models import cifar10_cnn_benchmark
from models import mnist_irnn_benchmark
from models import lstm_text_generation_benchmark
import upload_benchmarks_bq as bq
import argparse
import keras
import json

if keras.backend.backend() == "tensorflow":
  import tensorflow as tf
if keras.backend.backend() == "theano":
  import theano
if keras.backend.backend() == "cntk":
  import cntk

parser = argparse.ArgumentParser()
parser.add_argument('--mode',
                    help='The benchmark can be run on cpu, gpu and multiple gpus.')

args = parser.parse_args()

# Load the json config file for the requested mode.
config_file = open("benchmarks/scripts/keras_benchmarks/config.json", 'r')
config_contents = config_file.read()
config = json.loads(config_contents)[args.mode]


def get_backend_version():
    if keras.backend.backend() == "tensorflow":
        return tf.__version__
    if keras.backend.backend() == "theano":
        return theano.__version__
    if keras.backend.backend() == "cntk":
        return cntk.__version__
    return "undefined"


def _upload_metrics(current_model):
    bq.upload_metrics_to_bq(test_name=current_model.get_testname(),
                            total_time=current_model.get_totaltime(),
                            epochs=current_model.get_iters(),
                            batch_size=current_model.get_batch_size(),
                            backend_type=keras.backend.backend(),
                            backend_version=get_backend_version(),
                            cpu_num_cores=config['cpu_num_cores'],
                            cpu_memory=config['cpu_memory'],
                            cpu_memory_info=config['cpu_memory_info'],
                            gpu_count=config['gpus'],
                            gpu_platform=config['gpu_platform'],
                            platform_type=config['platform_type'],
                            platform_machine_type=config['platform_machine_type'],
                            keras_version=keras.__version__,
                            sample_type=current_model.get_sampletype())


# MNIST MLP
model = mnist_mlp_benchmark.MnistMlpBenchmark()
model.run_benchmark(gpus=config['gpus'])
_upload_metrics(model)

# CIFAR10 CNN
model = cifar10_cnn_benchmark.Cifar10CnnBenchmark()
model.run_benchmark(gpus=config['gpus'])
_upload_metrics(model)

# MNIST RNN
model = mnist_irnn_benchmark.MnistIrnnBenchmark()
model.run_benchmark(gpus=config['gpus'])
_upload_metrics(model)

# LSTM
model = lstm_text_generation_benchmark.LstmTextGenBenchmark()
model.run_benchmark(gpus=config['gpus'])
_upload_metrics(model)