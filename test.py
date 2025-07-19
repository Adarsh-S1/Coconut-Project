import cv2
from ultralytics import YOLO
import os

vedio_name="Images and videos/3.mp4"
output_name="output3.mp4"
output_folder = "Output Video"
percentage=0.2

if not os.path.exists(output_folder):
    os.makedirs(output_folder,exist_ok=True)

output_path=os.path.join(output_folder, output_name)

# Load the YOLOv8 model (replace 'yolov8n.pt' with your model file if needed)
model = YOLO('best.pt')

# Assuming the model has a names attribute mapping class ids to class names.
class_names = model.model.names if hasattr(model, 'model') else model.names

# Open the input video file (or use a camera index, e.g. 0 for webcam)
cap = cv2.VideoCapture(vedio_name)  # Change to your video file or camera source

# Get video properties for output video writer
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO model inference on the frame
    results = model(frame)
    result = results[0]  # Process first result since we're dealing with one frame at a time
    
    # Manually draw bounding boxes with labels
    if result.boxes is not None:
        boxes = result.boxes.data.cpu().numpy()
        for box in boxes:
            # box contains: [x1, y1, x2, y2, score, class]
            x1, y1, x2, y2, score, cls = box

            if score > percentage:
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cls = int(cls)
                # Retrieve the class name using the class index
                label_name = class_names[cls] if class_names and cls in class_names else str(cls)
                # Draw rectangle for each detected object
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Draw label with class name and score
                label = f"{label_name}: {score:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Write the annotated frame to the output video
    out.write(frame)

    # (Optional) Display the frame in a window
    cv2.imshow("YOLOv8 Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
out.release()
cv2.destroyAllWindows()