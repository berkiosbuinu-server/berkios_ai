from berkios.learning.trainer.local_ml import detect_local_ml, environment_report

def test_environment_report_shape():
    r=environment_report()
    for key in ["torch","transformers","peft","accelerate","bitsandbytes","lora_ready"]:
        assert key in r

def test_lora_ready_is_consistent():
    a=detect_local_ml()
    assert a.lora_ready == (a.torch and a.transformers and a.peft)
