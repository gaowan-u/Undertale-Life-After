package com.undertale.afterlife.input

import android.graphics.RectF
import kotlin.math.hypot

class VirtualJoystick {

    companion object {
        const val JOYSTICK_X = 128f
        const val JOYSTICK_Y_FROM_BOTTOM = 240f
        const val RADIUS_RATIO = 0.9f
        const val BASE_SIZE = 150f
        const val TOP_SIZE = 80f
        const val DEAD_ZONE = 10f
        private const val GAME_HEIGHT = 1080f
    }

    val baseRect: RectF
    val topRect: RectF
    val radius: Float

    var dragging: Boolean = false
        private set
    var directionX: Float = 0f
        private set
    var directionY: Float = 0f
        private set

    private var touchPointerId: Int = -1

    init {
        val baseTop = GAME_HEIGHT - JOYSTICK_Y_FROM_BOTTOM - BASE_SIZE
        baseRect = RectF(JOYSTICK_X, baseTop, JOYSTICK_X + BASE_SIZE, baseTop + BASE_SIZE)
        radius = (BASE_SIZE / 2f) * RADIUS_RATIO

        val cx = baseRect.centerX()
        val cy = baseRect.centerY()
        topRect = RectF(cx - TOP_SIZE / 2f, cy - TOP_SIZE / 2f, cx + TOP_SIZE / 2f, cy + TOP_SIZE / 2f)
    }

    fun handleTouchDown(logicalX: Float, logicalY: Float, pointerId: Int): Boolean {
        if (baseRect.contains(logicalX, logicalY) || topRect.contains(logicalX, logicalY)) {
            dragging = true
            touchPointerId = pointerId
            updatePosition(logicalX, logicalY)
            return true
        }
        return false
    }

    fun handleTouchMove(logicalX: Float, logicalY: Float, pointerId: Int) {
        if (dragging && pointerId == touchPointerId) {
            updatePosition(logicalX, logicalY)
        }
    }

    fun handleTouchUp(pointerId: Int) {
        if (dragging && pointerId == touchPointerId) {
            dragging = false
            touchPointerId = -1
            reset()
        }
    }

    fun reset() {
        val cx = baseRect.centerX()
        val cy = baseRect.centerY()
        topRect.set(cx - TOP_SIZE / 2f, cy - TOP_SIZE / 2f, cx + TOP_SIZE / 2f, cy + TOP_SIZE / 2f)
        directionX = 0f
        directionY = 0f
        touchPointerId = -1
        dragging = false
    }

    private fun updatePosition(logicalX: Float, logicalY: Float) {
        var dx = logicalX - baseRect.centerX()
        var dy = logicalY - baseRect.centerY()
        val distance = hypot(dx.toDouble(), dy.toDouble()).toFloat()

        if (distance > radius && radius > 0f) {
            val ratio = radius / distance
            dx *= ratio
            dy *= ratio
        }

        val cx = baseRect.centerX()
        val cy = baseRect.centerY()
        topRect.set(cx + dx - TOP_SIZE / 2f, cy + dy - TOP_SIZE / 2f, cx + dx + TOP_SIZE / 2f, cy + dy + TOP_SIZE / 2f)

        if (distance > DEAD_ZONE) {
            directionX = dx / radius
            directionY = dy / radius
        } else {
            directionX = 0f
            directionY = 0f
        }
    }
}
