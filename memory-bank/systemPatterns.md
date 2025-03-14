# System Patterns

## PDF Processing Pipeline Architecture

### Core Components

1. **AWS Bedrock Integration**
   - Uses Claude 3 Sonnet model for text analysis
   - Implements robust error handling and retry logic
   - Includes rate limiting mechanisms

2. **Text Extraction Layer**
   - Primary Methods:
     - pdfplumber: Basic text extraction
     - Docling: Advanced preprocessing with OCR capabilities
   - Switchable extraction strategies

3. **Rate Limiting System**
   - Adaptive backoff mechanism
   - Per-minute rate limiting
   - Dynamic delay calculation based on consecutive failures
   - Configurable limits:
     ```python
     MAX_CALLS_PER_MINUTE = 10
     MIN_BACKOFF_TIME = 5
     MAX_RETRIES = 15
     ```

4. **Metrics System**
   - Weighted token similarity calculation
   - Text normalization
   - Ground truth comparison
   - Performance tracking

### Data Flow Patterns

1. **Document Processing Pipeline**
   ```
   PDF Input -> Text Extraction -> Preprocessing -> AI Processing -> JSON Output
   ```

2. **Batch Processing Pattern**
   - Processes documents in configurable batch sizes
   - Implements delays between batches
   - Maintains progress tracking

3. **Error Handling Pattern**
   ```
   Try Operation -> Check for Throttling -> 
   Exponential Backoff -> Retry -> Max Retries Check
   ```

### Configuration Management

1. **Resource Limits**
   ```python
   MAX_TOKENS = 10000
   MAX_OUTPUT_TOKENS = 2000
   MAX_CONTEXT_WORDS = 150000
   MAX_OUTPUT_WORDS = 6200
   ```

2. **Processing Options**
   - OCR enablement options
   - Multiple prompt strategies
   - Configurable batch sizes

### Integration Patterns

1. **Google Drive Integration**
   - Mounted storage access
   - Persistent file management

2. **AWS Bedrock Integration**
   - Authentication handling
   - Service client management
   - Model-specific configurations

### Testing & Validation

1. **Similarity Metrics**
   - Token-based comparison
   - Weighted numerical token handling
   - Normalized text comparison

### Performance Optimization

1. **Rate Limiting Strategy**
   - Adaptive delays
   - Consecutive failure tracking
   - Dynamic backoff calculation

2. **Batch Processing Optimization**
   - Configurable batch sizes
   - Inter-batch delays
   - Progress tracking