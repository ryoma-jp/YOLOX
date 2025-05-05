FROM nvcr.io/nvidia/pytorch:24.07-py3

RUN apt update && \
    apt install -y libgl1-mesa-glx

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN pip uninstall -y opencv && \
    rm -rf /usr/local/lib/python3.10/dist-packages/cv2/ && \
    pip install opencv-python==4.9.0.80

ARG USER_ID
ARG GROUP_ID
ARG USER_NAME
RUN groupadd -g ${GROUP_ID} ${USER_NAME} && \
        useradd -m -u ${USER_ID} -g ${GROUP_ID} ${USER_NAME}
