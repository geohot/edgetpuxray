#include <edgetpu.h>
#include <assert.h>
#include "tensorflow/lite/interpreter.h"
#include "tensorflow/lite/kernels/register.h"
#include "tensorflow/lite/model.h"
#include "tensorflow/lite/optional_debug_tools.h"

int main(int argc, char* argv[]) {
  std::string model_file_name = "/Users/taylor/fun/edgetpu/libcoral/test_data/inception_v4_299_quant_edgetpu.tflite";
  auto tpu_context = edgetpu::EdgeTpuManager::GetSingleton()->OpenDevice();
  printf("open device\n");

  std::unique_ptr<tflite::Interpreter> interpreter;
  tflite::ops::builtin::BuiltinOpResolver resolver;
  auto model = tflite::FlatBufferModel::BuildFromFile(model_file_name.c_str());
  printf("model loaded\n");

  resolver.AddCustom(edgetpu::kCustomOp, edgetpu::RegisterCustomOp());
  tflite::InterpreterBuilder(*model, resolver)(&interpreter);
  interpreter->SetExternalContext(kTfLiteEdgeTpuContext, tpu_context.get());
  printf("did boilerplate\n");

  interpreter->AllocateTensors();
  interpreter->Invoke();
  printf("ran model (first)\n");

  printf("inputs: %lu outputs: %lu\n", interpreter->inputs().size(), interpreter->outputs().size());
  printf("in[0]: %s  out[0]: %s\n", interpreter->GetInputName(0), interpreter->GetOutputName(0));

  FILE *f = fopen(argv[1], "rb");
  auto *input = interpreter->typed_input_tensor<uint8_t>(0);
  assert(input != NULL);
  int len = fread(input, 1, 299*299*3, f);
  printf("read %d\n", len);
  fclose(f);

  interpreter->Invoke();
  printf("ran model (again)\n");

  //TfLiteTensor *tens = interpreter->output_tensor(0);

  const auto *const output = interpreter->typed_output_tensor<uint8_t>(0);
  printf("output ptr: %p\n", output);
  const auto outputSize = 1000;
  for (auto c=0u; c<outputSize; ++c) { if (output[c] > 0) printf("%d: %d\n", c, output[c]); }

  //cv::Mat img = cv::imread("banana.jpg", cv::IMREAD_GRAYSCALE);

  /*const auto outputSize = 10; // Also MNIST
  const auto *const output = interpreter->typed_output_tensor<int>(0);
  for (auto c=0u; c<outputSize; ++c) { printf("%d\n", output[c]); }
  printf("\n");*/

  interpreter.reset();
  tpu_context.reset();
  printf("shutdown\n");
}


