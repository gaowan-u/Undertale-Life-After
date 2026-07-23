package com.undertale.afterlife.input

import android.graphics.RectF
import android.view.KeyEvent

class ActionButtons {

    companion object {
        const val BTN1_X = 1400f
        const val BTN2_X = 1544f
        const val BTN3_X = 1688f
        const val BTN_Y_FROM_BOTTOM = 240f
        const val BTN2_Y_FROM_BOTTOM = 320f
        const val BTN3_Y_FROM_BOTTOM = 400f
        const val BTN_SIZE = 80f

        const val BACK_LEFT = 50f
        const val BACK_TOP = 50f
        const val BACK_WIDTH = 120f
        const val BACK_HEIGHT = 50f

        private const val GAME_HEIGHT = 1080f

        fun keyCodeFor(btnId: Int): Int = when (btnId) {
            1 -> KeyEvent.KEYCODE_Z
            2 -> KeyEvent.KEYCODE_X
            3 -> KeyEvent.KEYCODE_C
            else -> -1
        }
    }

    val btn1Rect: RectF
    val btn2Rect: RectF
    val btn3Rect: RectF
    val backRect: RectF

    val states: MutableMap<Int, Int> = mutableMapOf(1 to 0, 2 to 0, 3 to 0)
    val pressed: MutableMap<String, Boolean> = mutableMapOf(
        "1" to false, "2" to false, "3" to false, "back" to false
    )

    private val touchPointerIds: MutableMap<String, Int> = mutableMapOf()
    private var mousePressedBtn: String? = null
    private var mouseHeld: Boolean = false

    init {
        btn1Rect = RectF(BTN1_X, GAME_HEIGHT - BTN_Y_FROM_BOTTOM - BTN_SIZE, BTN1_X + BTN_SIZE, GAME_HEIGHT - BTN_Y_FROM_BOTTOM)
        btn2Rect = RectF(BTN2_X, GAME_HEIGHT - BTN2_Y_FROM_BOTTOM - BTN_SIZE, BTN2_X + BTN_SIZE, GAME_HEIGHT - BTN2_Y_FROM_BOTTOM)
        btn3Rect = RectF(BTN3_X, GAME_HEIGHT - BTN3_Y_FROM_BOTTOM - BTN_SIZE, BTN3_X + BTN_SIZE, GAME_HEIGHT - BTN3_Y_FROM_BOTTOM)
        backRect = RectF(BACK_LEFT, BACK_TOP, BACK_LEFT + BACK_WIDTH, BACK_TOP + BACK_HEIGHT)
    }

    fun resetFrameStates() {
        states[1] = 0
        states[2] = 0
        states[3] = 0
        pressed["back"] = false
    }

    fun updateHold(keysPressed: Set<Int>) {
        mouseHeld = mousePressedBtn != null

        for (btnId in listOf(1, 2, 3)) {
            val key = btnId.toString()
            if (pressed[key] == true) {
                if (touchPointerIds.containsKey(key) ||
                    (mouseHeld && mousePressedBtn == key) ||
                    keysPressed.contains(keyCodeFor(btnId))
                ) {
                    states[btnId] = 1
                } else {
                    pressed[key] = false
                }
            }
        }

        if (pressed["back"] == true && !touchPointerIds.containsKey("back") && !mouseHeld) {
            pressed["back"] = false
        }

        for ((btnId, key) in listOf(1 to KeyEvent.KEYCODE_Z, 2 to KeyEvent.KEYCODE_X, 3 to KeyEvent.KEYCODE_C)) {
            val k = btnId.toString()
            if (pressed[k] == true && !keysPressed.contains(key) && !touchPointerIds.containsKey(k)) {
                pressed[k] = false
            }
        }
    }

    private fun hitTest(logicalX: Float, logicalY: Float): String? {
        if (backRect.contains(logicalX, logicalY)) return "back"
        if (btn1Rect.contains(logicalX, logicalY)) return "1"
        if (btn2Rect.contains(logicalX, logicalY)) return "2"
        if (btn3Rect.contains(logicalX, logicalY)) return "3"
        return null
    }

    fun handleTouchDown(logicalX: Float, logicalY: Float, pointerId: Int) {
        val btn = hitTest(logicalX, logicalY) ?: return
        touchPointerIds[btn] = pointerId
        pressButton(btn)
    }

    fun handleTouchMove(logicalX: Float, logicalY: Float, pointerId: Int) {
        val newBtn = hitTest(logicalX, logicalY)

        val currentBtn = touchPointerIds.entries.firstOrNull { it.value == pointerId }?.key

        if (newBtn != currentBtn) {
            currentBtn?.let { releaseButton(it) }
            touchPointerIds.remove(currentBtn)
            if (newBtn != null) {
                touchPointerIds[newBtn] = pointerId
                pressButton(newBtn)
            }
        }
    }

    fun handleTouchUp(pointerId: Int) {
        val btn = touchPointerIds.entries.firstOrNull { it.value == pointerId }?.key
        if (btn != null) {
            releaseButton(btn)
            touchPointerIds.remove(btn)
        }
    }

    fun handleMouseDown(logicalX: Float, logicalY: Float) {
        val btn = hitTest(logicalX, logicalY) ?: return
        mousePressedBtn = btn
        pressButton(btn)
    }

    fun handleMouseUp() {
        val btn = mousePressedBtn
        if (btn != null) {
            releaseButton(btn)
            mousePressedBtn = null
        }
    }

    fun handleKeyDown(keyCode: Int) {
        when (keyCode) {
            KeyEvent.KEYCODE_Z -> { pressed["1"] = true; states[1] = 1 }
            KeyEvent.KEYCODE_X -> { pressed["2"] = true; states[2] = 1 }
            KeyEvent.KEYCODE_C -> { pressed["3"] = true; states[3] = 1 }
        }
    }

    fun handleKeyUp(keyCode: Int) {
        when (keyCode) {
            KeyEvent.KEYCODE_Z -> { pressed["1"] = false; states[1] = 0 }
            KeyEvent.KEYCODE_X -> { pressed["2"] = false; states[2] = 0 }
            KeyEvent.KEYCODE_C -> { pressed["3"] = false; states[3] = 0 }
        }
    }

    fun handleBackTouchDown(logicalX: Float, logicalY: Float, pointerId: Int): Boolean {
        if (backRect.contains(logicalX, logicalY)) {
            touchPointerIds["back"] = pointerId
            pressed["back"] = true
            return true
        }
        return false
    }

    fun handleBackTouchUp(pointerId: Int) {
        if (touchPointerIds["back"] == pointerId) {
            pressed["back"] = false
            touchPointerIds.remove("back")
        }
    }

    fun handleBackMouseDown(logicalX: Float, logicalY: Float): Boolean {
        if (backRect.contains(logicalX, logicalY)) {
            mousePressedBtn = "back"
            pressed["back"] = true
            return true
        }
        return false
    }

    private fun pressButton(btn: String) {
        pressed[btn] = true
        val intBtn = btn.toIntOrNull()
        if (intBtn != null) {
            states[intBtn] = 1
        }
    }

    private fun releaseButton(btn: String) {
        pressed[btn] = false
        val intBtn = btn.toIntOrNull()
        if (intBtn != null) {
            states[intBtn] = 0
        }
    }
}
