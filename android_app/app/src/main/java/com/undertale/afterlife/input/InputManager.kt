package com.undertale.afterlife.input

import android.view.KeyEvent
import android.view.MotionEvent
import com.undertale.afterlife.render.GameRenderer

class InputManager(private val renderer: GameRenderer) {

    val joystick = VirtualJoystick()
    val buttons = ActionButtons()

    val keysPressed: MutableSet<Int> = mutableSetOf()

    var mouseLogicalX: Float = 0f
        private set
    var mouseLogicalY: Float = 0f
        private set
    var mouseDown: Boolean = false
        private set

    fun resetFrameStates() {
        buttons.resetFrameStates()
    }

    fun updateHold() {
        buttons.updateHold(keysPressed)
    }

    fun handleTouchEvent(event: MotionEvent): Boolean {
        val action = event.actionMasked
        val pointerIndex = event.actionIndex
        val pointerId = event.getPointerId(pointerIndex)

        val screenX = event.getX(pointerIndex)
        val screenY = event.getY(pointerIndex)
        val (logicalX, logicalY) = renderer.screenToLogical(screenX.toInt(), screenY.toInt())

        when (action) {
            MotionEvent.ACTION_DOWN,
            MotionEvent.ACTION_POINTER_DOWN -> {
                mouseLogicalX = logicalX; mouseLogicalY = logicalY
                mouseDown = true

                buttons.handleTouchDown(logicalX, logicalY, pointerId)

                joystick.handleTouchDown(logicalX, logicalY, pointerId)
            }

            MotionEvent.ACTION_MOVE -> {
                for (i in 0 until event.pointerCount) {
                    val pid = event.getPointerId(i)
                    val sx = event.getX(i)
                    val sy = event.getY(i)
                    val (lx, ly) = renderer.screenToLogical(sx.toInt(), sy.toInt())

                    if (pid == 0) { mouseLogicalX = lx; mouseLogicalY = ly }

                    joystick.handleTouchMove(lx, ly, pid)
                    buttons.handleTouchMove(lx, ly, pid)
                }
            }

            MotionEvent.ACTION_UP,
            MotionEvent.ACTION_POINTER_UP -> {
                mouseDown = event.pointerCount > 1 || action != MotionEvent.ACTION_UP

                joystick.handleTouchUp(pointerId)
                buttons.handleTouchUp(pointerId)

                if (action == MotionEvent.ACTION_UP) {
                    mouseDown = false
                }
            }

            MotionEvent.ACTION_CANCEL -> {
                joystick.reset()
                mouseDown = false
            }
        }

        return true
    }

    fun handleKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        keysPressed.add(keyCode)

        when (keyCode) {
            KeyEvent.KEYCODE_Z, KeyEvent.KEYCODE_X, KeyEvent.KEYCODE_C -> {
                buttons.handleKeyDown(keyCode)
                return true
            }
        }

        return false
    }

    fun handleKeyUp(keyCode: Int, event: KeyEvent): Boolean {
        keysPressed.remove(keyCode)

        when (keyCode) {
            KeyEvent.KEYCODE_Z, KeyEvent.KEYCODE_X, KeyEvent.KEYCODE_C -> {
                buttons.handleKeyUp(keyCode)
                return true
            }
        }

        return false
    }

    fun getDirectionX(): Float {
        val kx = if (keysPressed.contains(KeyEvent.KEYCODE_DPAD_RIGHT) || keysPressed.contains(KeyEvent.KEYCODE_D)) 1f
            else if (keysPressed.contains(KeyEvent.KEYCODE_DPAD_LEFT) || keysPressed.contains(KeyEvent.KEYCODE_A)) -1f
            else 0f
        return if (kx != 0f) kx else joystick.directionX
    }

    fun getDirectionY(): Float {
        val ky = if (keysPressed.contains(KeyEvent.KEYCODE_DPAD_DOWN) || keysPressed.contains(KeyEvent.KEYCODE_S)) 1f
            else if (keysPressed.contains(KeyEvent.KEYCODE_DPAD_UP) || keysPressed.contains(KeyEvent.KEYCODE_W)) -1f
            else 0f
        return if (ky != 0f) ky else joystick.directionY
    }
}
