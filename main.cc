#include <edgetpu.h>
#include <dlfcn.h>
#include <assert.h>
#include "tensorflow/lite/interpreter.h"
#include "tensorflow/lite/kernels/register.h"
#include "tensorflow/lite/model.h"
#include "tensorflow/lite/optional_debug_tools.h"
#include <libusb.h>

void hexdump(void *d, int l) {
  for (int i = 0;i<l;i++) {
    if (i % 0x20 == 0 && i != 0)printf("\n");
    printf("%02x ", ((unsigned char*)d)[i]);
  }
  printf("\n");
}

extern "C" {

int (*REAL_libusb_control_transfer)(libusb_device_handle *dev_handle, uint8_t bmRequestType,
    uint8_t bRequest, uint16_t wValue, uint16_t wIndex, unsigned char *data,
    uint16_t wLength, unsigned int timeout) = NULL;
int libusb_control_transfer(libusb_device_handle *dev_handle, uint8_t bmRequestType,
    uint8_t bRequest, uint16_t wValue, uint16_t wIndex, unsigned char *data,
    uint16_t wLength, unsigned int timeout) {
  if (REAL_libusb_control_transfer == NULL) REAL_libusb_control_transfer = reinterpret_cast<decltype(REAL_libusb_control_transfer)>(dlsym(RTLD_NEXT, "libusb_control_transfer"));
  printf("libusb_control_transfer(0x%x, %d, reg:0x%6x, %p, wLength: %d) : ", bmRequestType, bRequest, (wIndex<<16) | wValue, data, wLength);
  auto ret = REAL_libusb_control_transfer(dev_handle, bmRequestType, bRequest, wValue, wIndex, data, wLength, timeout);
  hexdump(data, wLength);
  return ret;
}

/*void (*real_callback)(struct libusb_transfer *ptr) = NULL;
void callback(struct libusb_transfer *ptr) {
  printf("CALLBACK %d\n", ptr->endpoint);
  real_callback(ptr);
}*/

int (*REAL_libusb_submit_transfer)(struct libusb_transfer *ptr);
int libusb_submit_transfer(struct libusb_transfer *ptr) {
  if (REAL_libusb_submit_transfer == NULL) REAL_libusb_submit_transfer = reinterpret_cast<decltype(REAL_libusb_submit_transfer)>(dlsym(RTLD_NEXT, "libusb_submit_transfer"));
  //printf("%p\n", ptr);
  printf("endpoint:%2x type:%d length:%6x : ", ptr->endpoint, ptr->type, ptr->length);
  hexdump(ptr->buffer, (ptr->length > 0x20) ? 0x20 : ptr->length);
  if (ptr->length == 0x3fc20) {
    FILE *f = fopen("data/program.dump", "wb");
    fwrite(ptr->buffer, 1, ptr->length, f);
    fclose(f);
  }
  /*real_callback = ptr->callback;
  ptr->callback = callback;*/
  return REAL_libusb_submit_transfer(ptr);
}


}

int main(int argc, char* argv[]) {
  std::string model_file_name = "/Users/taylor/fun/edgetpu/libcoral/test_data/inception_v4_299_quant_edgetpu.tflite";
  auto tpu_context = edgetpu::EdgeTpuManager::GetSingleton()->OpenDevice();
  printf("opened device\n");

  std::unique_ptr<tflite::Interpreter> interpreter;
  tflite::ops::builtin::BuiltinOpResolver resolver;
  auto model = tflite::FlatBufferModel::BuildFromFile(model_file_name.c_str());
  printf("model loaded\n");

  resolver.AddCustom(edgetpu::kCustomOp, edgetpu::RegisterCustomOp());
  tflite::InterpreterBuilder(*model, resolver)(&interpreter);
  interpreter->SetExternalContext(kTfLiteEdgeTpuContext, tpu_context.get());
  printf("did boilerplate\n");

  interpreter->AllocateTensors();
  printf("allocated tensors\n");
  interpreter->Invoke();
  printf("ran model (first)\n");

  printf("inputs: %lu outputs: %lu\n", interpreter->inputs().size(), interpreter->outputs().size());
  printf("in[0]: %s  out[0]: %s\n", interpreter->GetInputName(0), interpreter->GetOutputName(0));

  FILE *f = fopen(argv[1], "rb");
  auto *input = interpreter->typed_input_tensor<uint8_t>(0);
  assert(input != NULL);
  int len = fread(input, 1, 299*299*3, f);
  printf("read 0x%x\n", len);
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


