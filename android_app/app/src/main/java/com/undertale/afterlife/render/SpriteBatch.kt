package com.undertale.afterlife.render

import android.opengl.GLES20
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.FloatBuffer
import java.nio.ShortBuffer

class SpriteBatch(private val maxSprites: Int = 2048) {

    companion object {
        private const val FLOATS_PER_VERTEX = 5
        private const val VERTICES_PER_SPRITE = 4
        private const val INDICES_PER_SPRITE = 6

        private val VERTEX_SHADER = """
            uniform mat4 u_projection;
            attribute vec4 a_position;
            attribute vec2 a_texCoord;
            attribute float a_alpha;
            varying vec2 v_texCoord;
            varying float v_alpha;
            void main() {
                gl_Position = u_projection * a_position;
                v_texCoord = a_texCoord;
                v_alpha = a_alpha;
            }
        """.trimIndent()

        private val FRAGMENT_SHADER = """
            precision mediump float;
            uniform sampler2D u_texture;
            varying vec2 v_texCoord;
            varying float v_alpha;
            void main() {
                vec4 color = texture2D(u_texture, v_texCoord);
                gl_FragColor = vec4(color.rgb, color.a * v_alpha);
            }
        """.trimIndent()
    }

    val shader = ShaderProgram(VERTEX_SHADER, FRAGMENT_SHADER)

    private val uProjection: Int = shader.getUniformLocation("u_projection")
    private val uTexture: Int = shader.getUniformLocation("u_texture")
    private val aPosition: Int = shader.getAttribLocation("a_position")
    private val aTexCoord: Int = shader.getAttribLocation("a_texCoord")
    private val aAlpha: Int = shader.getAttribLocation("a_alpha")

    private val maxVertices = maxSprites * VERTICES_PER_SPRITE
    private val vertexData = FloatArray(maxVertices * FLOATS_PER_VERTEX)
    private val vertexBuffer: FloatBuffer = ByteBuffer
        .allocateDirect(maxVertices * FLOATS_PER_VERTEX * 4)
        .order(ByteOrder.nativeOrder())
        .asFloatBuffer()
    private val indexBuffer: ShortBuffer

    private var spriteCount = 0
    private var currentTexture: Texture? = null
    private var drawing = false

    init {
        val indices = ShortArray(maxSprites * INDICES_PER_SPRITE)
        for (i in 0 until maxSprites) {
            val vi = i * INDICES_PER_SPRITE
            val base = (i * VERTICES_PER_SPRITE).toShort()
            indices[vi] = base
            indices[vi + 1] = (base + 1).toShort()
            indices[vi + 2] = (base + 2).toShort()
            indices[vi + 3] = base
            indices[vi + 4] = (base + 2).toShort()
            indices[vi + 5] = (base + 3).toShort()
        }
        indexBuffer = ByteBuffer
            .allocateDirect(indices.size * 2)
            .order(ByteOrder.nativeOrder())
            .asShortBuffer()
        indexBuffer.put(indices)
        indexBuffer.flip()
    }

    fun begin(projectionMatrix: FloatArray) {
        if (drawing) {
            throw IllegalStateException("SpriteBatch.end() must be called before begin()")
        }
        drawing = true
        spriteCount = 0
        currentTexture = null

        shader.use()
        GLES20.glUniformMatrix4fv(uProjection, 1, false, projectionMatrix, 0)
        GLES20.glUniform1i(uTexture, 0)
    }

    fun draw(
        texture: Texture,
        dstX: Float,
        dstY: Float,
        dstW: Float = texture.width.toFloat(),
        dstH: Float = texture.height.toFloat(),
        srcX: Float = 0f,
        srcY: Float = 0f,
        srcW: Float = 0f,
        srcH: Float = 0f,
        alpha: Float = 1f,
        flipX: Boolean = false,
        flipY: Boolean = false
    ) {
        if (!drawing) {
            throw IllegalStateException("Must call begin() before draw()")
        }

        if (currentTexture !== texture) {
            flush()
            currentTexture = texture
        }

        if (spriteCount >= maxSprites) {
            flush()
        }

        var u1: Float
        var v1: Float
        var u2: Float
        var v2: Float
        if (srcW <= 0f || srcH <= 0f) {
            u1 = 0f; v1 = 0f
            u2 = 1f; v2 = 1f
        } else {
            val tw = texture.width.toFloat()
            val th = texture.height.toFloat()
            u1 = srcX / tw; v1 = srcY / th
            u2 = (srcX + srcW) / tw; v2 = (srcY + srcH) / th
        }

        if (flipX) { val t = u1; u1 = u2; u2 = t }
        if (flipY) { val t = v1; v1 = v2; v2 = t }

        val x2 = dstX + dstW
        val y2 = dstY + dstH

        val offset = spriteCount * VERTICES_PER_SPRITE * FLOATS_PER_VERTEX

        vertexData[offset] = dstX
        vertexData[offset + 1] = dstY
        vertexData[offset + 2] = u1
        vertexData[offset + 3] = v1
        vertexData[offset + 4] = alpha

        vertexData[offset + 5] = x2
        vertexData[offset + 6] = dstY
        vertexData[offset + 7] = u2
        vertexData[offset + 8] = v1
        vertexData[offset + 9] = alpha

        vertexData[offset + 10] = x2
        vertexData[offset + 11] = y2
        vertexData[offset + 12] = u2
        vertexData[offset + 13] = v2
        vertexData[offset + 14] = alpha

        vertexData[offset + 15] = dstX
        vertexData[offset + 16] = y2
        vertexData[offset + 17] = u1
        vertexData[offset + 18] = v2
        vertexData[offset + 19] = alpha

        spriteCount++
    }

    fun end() {
        if (!drawing) {
            throw IllegalStateException("Must call begin() before end()")
        }
        flush()
        drawing = false
    }

    private fun flush() {
        if (spriteCount == 0 || currentTexture == null) return

        currentTexture!!.bind()

        val vertexCount = spriteCount * VERTICES_PER_SPRITE
        val floatCount = vertexCount * FLOATS_PER_VERTEX
        val stride = FLOATS_PER_VERTEX * 4

        vertexBuffer.clear()
        vertexBuffer.put(vertexData, 0, floatCount)
        vertexBuffer.flip()

        vertexBuffer.position(0)
        GLES20.glVertexAttribPointer(
            aPosition, 2, GLES20.GL_FLOAT, false, stride, vertexBuffer
        )

        vertexBuffer.position(2)
        GLES20.glVertexAttribPointer(
            aTexCoord, 2, GLES20.GL_FLOAT, false, stride, vertexBuffer
        )

        vertexBuffer.position(4)
        GLES20.glVertexAttribPointer(
            aAlpha, 1, GLES20.GL_FLOAT, false, stride, vertexBuffer
        )

        GLES20.glEnableVertexAttribArray(aPosition)
        GLES20.glEnableVertexAttribArray(aTexCoord)
        GLES20.glEnableVertexAttribArray(aAlpha)

        val indexCount = spriteCount * INDICES_PER_SPRITE
        GLES20.glDrawElements(
            GLES20.GL_TRIANGLES, indexCount, GLES20.GL_UNSIGNED_SHORT, indexBuffer
        )

        GLES20.glDisableVertexAttribArray(aPosition)
        GLES20.glDisableVertexAttribArray(aTexCoord)
        GLES20.glDisableVertexAttribArray(aAlpha)

        spriteCount = 0
    }

    fun dispose() {
        shader.delete()
    }
}
