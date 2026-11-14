package com.undertale.afterlife

import android.content.Context
import android.opengl.GLSurfaceView
import android.view.KeyEvent
import android.view.MotionEvent
import com.undertale.afterlife.audio.AudioManager
import com.undertale.afterlife.input.InputManager
import com.undertale.afterlife.render.GameRenderer
import com.undertale.afterlife.save.SaveSystem

class GameView(context: Context) : GLSurfaceView(context) {

    companion object {
        const val GAME_WIDTH = 1920
        const val GAME_HEIGHT = 1080
    }

    val gameRenderer = GameRenderer()
    val inputManager = InputManager(gameRenderer)
    val saveSystem = SaveSystem(context)
    val audioManager = AudioManager(context.assets)
    val gameManager: GameManager

    init {
        setEGLContextClientVersion(2)
        setRenderer(gameRenderer)
        renderMode = RENDERMODE_CONTINUOUSLY

        gameManager = GameManager(context.assets, inputManager, saveSystem, audioManager)
        gameRenderer.setGameManager(gameManager)
    }

    override fun onPause() {
        super.onPause()
    }

    override fun onResume() {
        super.onResume()
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return inputManager.handleTouchEvent(event)
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        gameManager.onKeyJustPressed(keyCode)
        if (inputManager.handleKeyDown(keyCode, event)) {
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    override fun onKeyUp(keyCode: Int, event: KeyEvent): Boolean {
        if (inputManager.handleKeyUp(keyCode, event)) {
            return true
        }
        return super.onKeyUp(keyCode, event)
    }
}
