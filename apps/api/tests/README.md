# Weather Fortune API Tests

This directory contains comprehensive tests for the Weather Fortune API.

## Prerequisites

Make sure you have the required packages installed:

```bash
pip install pytest fastapi httpx
```

## Running Tests

From the `apps/api` directory:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_prediction_api.py

# Run specific test
pytest tests/test_prediction_api.py::TestPredictionAPI::test_short_term_prediction
```

## Test Coverage

### Core API Tests (`TestPredictionAPI`)

- ✅ Root endpoint functionality
- ✅ Short-term predictions (0-10 days)
- ✅ Medium-term predictions (10-15 days)
- ✅ Long-term predictions (30+ days)
- ✅ Uncertainty band validation
- ✅ Error handling for invalid inputs
- ✅ Extreme coordinate handling
- ✅ Parameter validation

### Climatology Tests (`TestClimatologyModel`)

- ✅ Seasonal variation effects
- ✅ Latitude-based temperature differences

## Test Data

Tests use real coordinates:

- **Borlänge, Sweden**: `60.4833, 15.4167`
- **Stockholm, Sweden**: `59.3293, 18.0686`
- **Copenhagen, Denmark**: `55.6761, 12.5683`
- **Svalbard, Norway**: `78.2232, 15.6267` (Arctic test)
- **Antarctica**: `-77.8419, 166.6863` (Antarctic test)

## Known Issues

Some edge case tests may fail due to:

- Date parsing edge cases
- API timeout issues with external services
- Climatology model limitations

These will be addressed as the API matures.
