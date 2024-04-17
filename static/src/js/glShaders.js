function applyShader() {
    const body = document.body;
    const canvas = document.createElement('canvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    body.appendChild(canvas);

    const gl = canvas.getContext('webgl');

    // Vertex shader code (a simple passthrough)
    const vertexShaderSource = `
        attribute vec2 a_position;
        void main() {
            gl_Position = vec4(a_position, 0, 1);
        }
    `;

    // Fragment shader code for generating curved waves in orange color
    const fragmentShaderSource = `
        precision highp float;

        uniform float u_time;
        uniform vec2 u_resolution;

        void main() {
            // Normalized coordinates
            vec2 st = gl_FragCoord.xy / u_resolution;

            // Apply curved waves effect based on time
            // float wave = abs(sin(u_time + st.y * 5.0) * 0.15);
            float wave = abs(sin(u_time + st.y * 5.0) * 0.15) * cos(st.x * 3.0 - u_time);

            // Orange color (r, g, b, a)
            vec4 orangeColor = vec4(1.0, 0.5, 0.0, 1.0);

            // Apply the wave effect to the color
            vec4 finalColor = orangeColor + vec4(wave, wave, wave, 0.0);

            gl_FragColor = finalColor;
        }
    `;

    // Create vertex shader
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vertexShader, vertexShaderSource);
    gl.compileShader(vertexShader);

    // Create fragment shader
    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fragmentShader, fragmentShaderSource);
    gl.compileShader(fragmentShader);

    // Create a shader program and link the shaders
    const shaderProgram = gl.createProgram();
    gl.attachShader(shaderProgram, vertexShader);
    gl.attachShader(shaderProgram, fragmentShader);
    gl.linkProgram(shaderProgram);
    gl.useProgram(shaderProgram);

    // Create a buffer for a square
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    const vertices = [-1, -1, -1, 1, 1, 1, 1, -1];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);

    // Get the position attribute location
    const positionAttributeLocation = gl.getAttribLocation(shaderProgram, "a_position");
    gl.enableVertexAttribArray(positionAttributeLocation);
    gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);

    // Set resolution uniform
    const resolutionUniformLocation = gl.getUniformLocation(shaderProgram, "u_resolution");
    gl.uniform2f(resolutionUniformLocation, canvas.width, canvas.height);

    // Animation loop
    let startTime = performance.now();
    function render() {
        // Update time uniform
        const timeUniformLocation = gl.getUniformLocation(shaderProgram, "u_time");
        const currentTime = performance.now();
        const elapsedTime = (currentTime - startTime) / 1000.0;
        gl.uniform1f(timeUniformLocation, elapsedTime);

        // Clear the canvas
        gl.clearColor(0.0, 0.0, 0.0, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT);

        // Draw the square
        gl.drawArrays(gl.TRIANGLE_FAN, 0, 4);

        // Request the next frame
        requestAnimationFrame(render);
    }

    // Start the animation loop
    render();
}
document.addEventListener("DOMContentLoaded", () => {
    applyShader();
});