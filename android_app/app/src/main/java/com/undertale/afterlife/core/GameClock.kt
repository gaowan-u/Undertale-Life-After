package com.undertale.afterlife.core

class GameClock {
    private var lastTime = 0L
    private var frameCount = 0
    private var fpsAccum = 0f
    private var currentFps = 0f

    var deltaTime: Float = 0f
        private set

    fun start() {
        lastTime = System.nanoTime()
        frameCount = 0
        fpsAccum = 0f
        deltaTime = 0f
    }

    fun update(): Float {
        val now = System.nanoTime()
        val deltaNs = now - lastTime
        lastTime = now
        deltaTime = deltaNs / 1_000_000_000f

        frameCount++
        fpsAccum += deltaTime
        if (fpsAccum >= 1f) {
            currentFps = frameCount / fpsAccum
            frameCount = 0
            fpsAccum = 0f
        }

        return deltaTime
    }

    fun getFps(): Float = currentFps
}
