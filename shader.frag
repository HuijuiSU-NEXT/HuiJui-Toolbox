
#version 460 core
#include <flutter/runtime_effect.glsl>

out vec4 fragColor;
uniform vec2 u_size;
uniform float u_time;

void main() {
    vec2 uv = FlutterFragCoord().xy / u_size;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_size.x / u_size.y;

    // 动态流体核心：多层正弦波扭曲
    float t = u_time * 0.15;
    p.x += sin(p.y * 3.0 + t) * 0.3;
    p.y += cos(p.x * 3.0 + t * 0.8) * 0.3;
    p.x += sin(p.y * 5.0 - t * 0.6) * 0.15;
    p.y += cos(p.x * 5.0 + t * 0.5) * 0.15;

    // 颜色混合 (浅青绿、浅黄、浅粉紫)
    vec3 c1 = vec3(0.65, 0.95, 0.85); // 薄荷绿
    vec3 c2 = vec3(1.0, 0.95, 0.6);   // 鹅黄
    vec3 c3 = vec3(0.85, 0.7, 0.95);  // 粉紫

    // 根据扭曲后的坐标混合颜色
    float mix1 = clamp(p.x * 0.8 + 0.5, 0.0, 1.0);
    float mix2 = clamp(p.y * 0.8 + 0.5, 0.0, 1.0);

    vec3 color = mix(c1, c2, mix1);
    color = mix(color, c3, mix2 * 0.7);

    // 添加一点亮度变化，增加通透感
    float brightness = 1.0 + sin(p.x * 2.0 + p.y * 2.0 + u_time) * 0.05;
    color *= brightness;

    fragColor = vec4(color, 1.0);
}
