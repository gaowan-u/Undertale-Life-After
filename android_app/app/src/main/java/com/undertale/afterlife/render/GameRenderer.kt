package com.undertale.afterlife.render

import android.opengl.GLES20
import android.opengl.GLSurfaceView
import android.opengl.Matrix
import com.undertale.afterlife.GameManager
import javax.microedition.khronos.egl.EGLConfig
import javax.microedition.khronos.opengles.GL10

class GameRenderer(
    private var gameManager: GameManager? = null
) : GLSurfaceView.Renderer {

    companion object {
        const val GAME_WIDTH = 1920f
        const val GAME_HEIGHT = 1080f
    }

    private val projectionMatrix = FloatArray(16)

    private lateinit var spriteBatch: SpriteBatch

    private var viewportX = 0
    private var viewportY = 0
    private var viewportW = 0
    private var viewportH = 0

    private var lastFrameNano: Long = 0L

    fun setGameManager(gm: GameManager) {
        gameManager = gm
    }

    override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
        GLES20.glClearColor(0f, 0f, 0f, 1f)
        GLES20.glEnable(GLES20.GL_BLEND)
        GLES20.glBlendFunc(GLES20.GL_SRC_ALPHA, GLES20.GL_ONE_MINUS_SRC_ALPHA)

        spriteBatch = SpriteBatch()
        lastFrameNano = System.nanoTime()
    }

    override fun onSurfaceChanged(gl: GL10?, width: Int, height: Int) {
        val scaleW = width / GAME_WIDTH
        val scaleH = height / GAME_HEIGHT
        val scale = minOf(scaleW, scaleH)

        val renderW = (GAME_WIDTH * scale).toInt()
        val renderH = (GAME_HEIGHT * scale).toInt()

        viewportX = (width - renderW) / 2
        viewportY = (height - renderH) / 2
        viewportW = renderW
        viewportH = renderH

        GLES20.glViewport(viewportX, viewportY, viewportW, viewportH)
        Matrix.orthoM(projectionMatrix, 0, 0f, GAME_WIDTH, GAME_HEIGHT, 0f, -1f, 1f)
    }

    override fun onDrawFrame(gl: GL10?) {
        val now = System.nanoTime()
        val deltaTime = (now - lastFrameNano) / 1_000_000_000f
        lastFrameNano = now

        val gm = gameManager
        if (gm != null) {
            gm.update(deltaTime)
        }

        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT)
        spriteBatch.begin(projectionMatrix)

        if (gm != null) {
            gm.draw(spriteBatch)
        }

        spriteBatch.end()
    }

    fun screenToLogical(screenX: Int, screenY: Int): Pair<Float, Float> {
        if (viewportW == 0) return 0f to 0f
        val scale = viewportW / GAME_WIDTH
        val logicalX = (screenX - viewportX) / scale
        val logicalY = (screenY - viewportY) / scale
        return logicalX to logicalY
    }

    fun getScale(): Float = if (viewportW > 0) viewportW / GAME_WIDTH else 1f

    fun dispose() {
        spriteBatch.dispose()
    }
}
