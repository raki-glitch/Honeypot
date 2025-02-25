# Llama-2 Kafka Fine-Tuning

## Overview
This project fine-tunes the LLaMA-2-7B model using real-time attack logs from Kafka, ensuring resilience against failures and automatic recovery.

## Key Enhancements & Why They Were Made

| **Feature**  | **Original Code** | **Enhanced Code** | **Why This Change?** |
|-------------|------------------|------------------|------------------|
| **Hugging Face Model Loading** | Direct `from_pretrained` without checkpoint checking | Checks for saved checkpoint in `save_path` before loading from Hugging Face | Ensures model resumes training from where it left off if the container restarts |
| **Trainer Implementation** | Manual training loop with `optimizer` and `loss.backward()` | Switched to `Trainer.train(resume_from_checkpoint=True)` | Trainer handles large datasets efficiently and ensures robust resumption |
| **Kafka Consumer Setup** | Basic Kafka consumer initialization | Added `num_workers=4` for faster processing and an async retry mechanism | Faster log consumption and automatic reconnection to Kafka if it's offline |
| **Kafka Connection Logging** | No clear indication of Kafka connection status | Added `logging.info("Kafka Consumer connected successfully.")` | Ensures visibility in Docker logs when Kafka successfully connects |
| **Training Resumption** | No resume support, fresh training each time | `resume_from_checkpoint=True` in `Trainer` and checkpoint loading in model initialization | Guarantees model resumes from the last saved state after a failure |
| **Asynchronous Kafka Handling** | Synchronous consumption loop | Introduced `asyncio.run(create_consumer())` and `asyncio.run(consume_kafka())` | Prevents blocking, handles Kafka downtime more smoothly |
| **Save Checkpoints Periodically** | Saves model every batch manually | Trainer auto-saves using `save_steps=500, save_total_limit=2` | Efficient checkpointing without manual intervention |
| **model.train()** | Not explicitly called | Added `model.train()` | Ensures dropout and layer normalization updates for proper fine-tuning |
| **optimizer.zero_grad()** | Not explicitly called before backpropagation | Added `optimizer.zero_grad()` before `loss.backward()` | Prevents gradient accumulation from previous iterations |
| **loss.backward() & optimizer.step()** | Not included in training logic | Added `loss.backward()` and `optimizer.step()` | Ensures gradients are computed and model weights are updated correctly |
| **Batch Size and Collecting Logs Before Training** | Processing single logs individually | Collects logs into batches before training | Stabilizes training, prevents overfitting, and optimizes GPU usage |
| **padding=True, truncation=True, max_length=512 in Tokenization** | Tokenization parameters not specified | Added padding, truncation, and max_length | Ensures logs have uniform length and fit within model input size |
| **labels=inputs["input_ids"] for Supervised Fine-Tuning** | Labels not explicitly set | Set `labels=inputs["input_ids"]` | Trains model to reproduce input, adapting it to attack logs |
| **os.makedirs(save_path) and Fixing the Save Path Issue** | No validation for save path existence | Ensures save path is a valid directory | Prevents failures if a file exists at the save path |
| **Using device = torch.device("cuda" if torch.cuda.is_available() else "cpu")** | Model and data not explicitly moved to GPU | Added device check and model/data transfer | Optimizes performance by utilizing GPU if available |
| **Periodic Model Saving (Only After a Batch)** | Model saved after every message | Saves model only after processing a batch | Prevents excessive disk writes and reduces performance overhead |

## Potential Issues Prevented
1. **Training Restarts from Scratch**  
   - Without checkpoint loading, if the container crashed, it would start from zero. Now, it **automatically resumes**.
   
2. **Kafka Connection Drops & Stalls Training**  
   - Previously, if Kafka was offline, the consumer would stop working. Now, it **retries indefinitely** until Kafka is back.
   
3. **Inefficient Training on Large Datasets**  
   - Using `Trainer` ensures more **optimized fine-tuning**, avoiding memory issues with large datasets.

4. **Hard to Debug Kafka Connectivity**  
   - Now, logs explicitly show **when Kafka is connected or retrying**.

## Deployment on Azure: Potential Issues & Solutions

| **Issue** | **Problem** | **Solution** |
|----------|------------|-------------|
| **Insufficient GPU Resources** | Azure GPU VMs (NC, ND-series) may not be available on demand | Use **Azure Machine Learning (AML) with auto-scaling** to allocate GPUs dynamically |
| **Kafka Connectivity Issues** | If using Azure Event Hubs (Kafka mode), network issues may cause timeouts | Use **private endpoints or Virtual Network (VNet) integration** for secure, low-latency access |
| **Slow Model Loading Due to Storage Latency** | Loading from Azure Blob Storage may be slow | Cache the model locally using **Azure Files (NFS) or Ephemeral Disks** for faster access |
| **Checkpoint Persistence in Stateless Containers** | If a container crashes, local checkpoints are lost | Store checkpoints in **Azure Blob Storage or Azure Files** for recovery |
| **Timeouts in Kafka Consumer with Auto-Scaling** | Kafka consumers may scale dynamically, causing offset issues | Configure **Kafka consumer groups and enable offset retention** in Event Hubs |
| **High Training Costs on Azure** | GPUs are expensive, and inefficient training increases costs | Use **spot instances with autoscaling** for cost efficiency |
| **Networking & Firewall Restrictions** | Azure security settings may block outbound access | Ensure **Hugging Face and Kafka brokers are accessible** via network rules |

## Final Verdict
🚀 **Now the system is fault-tolerant, efficient, and scalable for continuous AI training.**  
If the container crashes or Kafka goes down, it will **recover automatically without manual intervention**.  

### Next Steps
- Add monitoring and alerting for Kafka and training progress.
- Optimize batch sizes based on hardware constraints.
- Explore distributed training for improved efficiency.

