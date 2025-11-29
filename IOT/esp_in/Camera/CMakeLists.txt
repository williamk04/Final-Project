idf_component_register(
    SRCS "Camera.c"
    INCLUDE_DIRS "include"
    REQUIRES esp32-camera esp_http_client Wifi json
)
