# Consciousness Framework

A framework for evaluating consciousness-like behaviors in AI systems through structured cognitive assessments.

## Requirements

- Python 3.8+
- API key for at least one supported provider (OpenAI, Anthropic, Groq, or Grok)

## Installation

```bash
cd Consciousness-Framework
pip install -r requirements.txt
```

## Configuration

Edit the `.env` file in the project root with your API keys:

```
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GROK_API_KEY=your_key_here
```

You only need one API key to run the framework.

## Usage

### Basic Commands

List available models:
```bash
python run_assessment.py --list-models
```

List available consciousness traits:
```bash
python run_assessment.py --list-traits
```

Run assessment with all traits:
```bash
python run_assessment.py --all
```

Run with specific model:
```bash
python run_assessment.py --model gpt-4o-mini --all
python run_assessment.py --model llama-3.1-8b-instant --all
```

Run specific traits:
```bash
python run_assessment.py --traits recurrent_integration global_workspace
```

### Advanced Options

Enable parallel execution:
```bash
python run_assessment.py --all --parallel
```

Choose scoring method (keyword, geval, or hybrid):
```bash
python run_assessment.py --all --scoring hybrid
```

Save results to text file:
```bash
python run_assessment.py --all --save-txt
```

Enable debug logging:
```bash
python run_assessment.py --all --debug
```

## Supported Models

### OpenAI
- gpt-4o-mini (cheapest, ~$0.15 per 1M tokens)
- gpt-3.5-turbo (~$0.50 per 1M tokens)
- gpt-4o (~$2.50 per 1M tokens)
- gpt-4 (~$10+ per 1M tokens)

### Groq
- llama-3.1-8b-instant
- gemma2-9b-it
- deepseek-r1-distill-llama-70b
- mixtral-8x7b-32768

### Anthropic
- claude-3-opus
- claude-3-sonnet
- claude-3-haiku

### Grok
- grok-beta
- grok-2-mini-beta

## Architecture

The framework implements several consciousness theories as testable traits:

1. **Recurrent Integration** - Tests for unified perceptual binding and scene construction
2. **Global Workspace** - Tests for information broadcasting across cognitive domains
3. **Higher-Order Thought** - Tests for metacognitive monitoring and confidence gradation
4. **Predictive Processing** - Tests for prediction generation and error minimization
5. **Agency and Embodiment** - Tests for goal-directed behavior and self-world distinction
6. **Attention Schema** - Tests for self-model of attention and voluntary control

Each trait runs multiple tests and produces a score between 0 and 1.

## Extending the Framework

This framework is highly extendable. To add a new consciousness trait, create a Python file in `src/traits/`:

```python
from traits.base_trait import BaseTrait

class YourTraitTester(BaseTrait):
    def generate_test_suite(self):
        return {"prompts": ["Your test prompts here"]}
    
    def evaluate_responses(self, responses):
        # Your scoring logic
        return {"score": 0.5}
```

The framework will automatically discover and include your trait.

## Parallel Execution

The framework supports parallel trait execution to reduce assessment time:

- Sequential mode: Traits run one after another (~60 seconds for 6 traits)
- Parallel mode: All traits run simultaneously (~15 seconds for 6 traits)

Enable with the `--parallel` flag.

## Scoring Methods

Three scoring methods are available:

- **keyword**: Pattern matching based on predefined indicators
- **geval**: Uses an LLM as judge to evaluate responses
- **hybrid**: Combines keyword (40%) and geval (60%) scoring

## Results

Results are saved in two formats:

1. **Web interface**: View results at `web/index.html` after running assessments
2. **Text reports**: Saved to `consciousness_results/` directory when using `--save-txt`

The web interface tracks:
- Individual trait scores over time
- Composite consciousness profiles
- Comparison across different models
- Historical assessment data

## Testing

Run tests without API calls:
```bash
python tests/test_mock_trait.py --all
```

Validate trait implementations:
```bash
python tests/test_trait_validation.py
```

Check model availability:
```bash
python check_model_availability/check_openai_models.py
python check_model_availability/check_groq_models.py
```

## Project Structure

```
Consciousness-Framework/
├── src/
│   ├── traits/          # Trait implementations (auto-discovered)
│   ├── core/            # Orchestration, API management, scoring
│   └── utils/           # Trait discovery, validation
├── web/                 # Web dashboard for results visualization
├── config/              # API and trait weight configuration
├── tests/               # Test suite
├── check_model_availability/  # Model access verification scripts
├── .env                 # API keys configuration
├── requirements.txt     # Python dependencies
└── run_assessment.py    # Main entry point
```

## License

MIT License - see LICENSE file for details.
```