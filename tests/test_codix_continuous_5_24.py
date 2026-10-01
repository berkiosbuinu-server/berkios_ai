from berkios.learning.continuous import CodixContinuousLearningLoop, LoopConfig, LoopState

def test_continuous_success(tmp_path):
    loop=CodixContinuousLearningLoop(tmp_path,LoopConfig(min_new_examples=2,min_validation_score=.8))
    r=loop.run_once(
        collect=lambda:[1,2],
        build_dataset=lambda x: {"examples":x},
        train=lambda d: {"version":"0.2"},
        evaluate=lambda m: {"score":.91},
        baseline_score=.90,
    )
    assert r.state==LoopState.COMPLETED
    assert r.version=="0.2"

def test_insufficient_data(tmp_path):
    loop=CodixContinuousLearningLoop(tmp_path,LoopConfig(min_new_examples=3))
    r=loop.run_once(
        collect=lambda:[1],
        build_dataset=lambda x:{},
        train=lambda d:{"version":"x"},
        evaluate=lambda m:{"score":1},
    )
    assert r.state==LoopState.REJECTED

def test_regression(tmp_path):
    loop=CodixContinuousLearningLoop(tmp_path,LoopConfig(min_new_examples=1,max_regression=.02))
    r=loop.run_once(
        collect=lambda:[1],
        build_dataset=lambda x:{},
        train=lambda d:{"version":"x"},
        evaluate=lambda m:{"score":.70},
        baseline_score=.90,
    )
    assert r.state==LoopState.REJECTED
