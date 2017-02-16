Although we are working heavily to make this demo public, there are many tasks yet to be accomplished.

Please come back after we clean up repository and verify everything is consistent.
It is plan to be ready in early March.

---
![](./setup/image/demo_overview.png)

## Serving mode
- Android tablet: for UI, recognizes the voice command with Speech and NL API
- Controller PC (Linux) and camera: recognizes the candies with Cloud ML, controls the robot arm
- Robot arm: picks the candy

## Learning mode
- Android tablet: shows UI for training process updates
- Controller PC: runs Inception-v3 + transfer learning on Cloud ML to train a model from scratch, with the camera image
