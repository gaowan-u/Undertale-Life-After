package com.undertale.afterlife.render

import android.content.res.AssetManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.opengl.GLES20
import android.opengl.GLUtils

class Texture {
    var textureId: Int = 0
        private set
    var width: Int = 0
        private set
    var height: Int = 0
        private set

    companion object {
        fun createSolidColor(r: Int, g: Int, b: Int, a: Int = 255): Texture {
            val bitmap = Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
            bitmap.setPixel(0, 0, (a shl 24) or (r shl 16) or (g shl 8) or b)
            val texture = Texture()
            texture.loadFromBitmap(bitmap)
            bitmap.recycle()
            return texture
        }

        fun createSolidColorARGB(argb: Int): Texture {
            val bitmap = Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
            bitmap.setPixel(0, 0, argb)
            val texture = Texture()
            texture.loadFromBitmap(bitmap)
            bitmap.recycle()
            return texture
        }
    }

    fun load(assetManager: AssetManager, path: String) {
        val inputStream = assetManager.open(path)
        val bitmap = BitmapFactory.decodeStream(inputStream)
        inputStream.close()

        if (bitmap == null) {
            throw RuntimeException("Failed to load texture: $path")
        }

        loadFromBitmap(bitmap)
        bitmap.recycle()
    }

    fun loadFromBitmap(bitmap: android.graphics.Bitmap) {
        width = bitmap.width
        height = bitmap.height

        val textures = IntArray(1)
        GLES20.glGenTextures(1, textures, 0)
        textureId = textures[0]

        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textureId)
        GLES20.glTexParameteri(
            GLES20.GL_TEXTURE_2D,
            GLES20.GL_TEXTURE_MIN_FILTER,
            GLES20.GL_NEAREST
        )
        GLES20.glTexParameteri(
            GLES20.GL_TEXTURE_2D,
            GLES20.GL_TEXTURE_MAG_FILTER,
            GLES20.GL_NEAREST
        )
        GLES20.glTexParameteri(
            GLES20.GL_TEXTURE_2D,
            GLES20.GL_TEXTURE_WRAP_S,
            GLES20.GL_CLAMP_TO_EDGE
        )
        GLES20.glTexParameteri(
            GLES20.GL_TEXTURE_2D,
            GLES20.GL_TEXTURE_WRAP_T,
            GLES20.GL_CLAMP_TO_EDGE
        )

        GLUtils.texImage2D(GLES20.GL_TEXTURE_2D, 0, bitmap, 0)

        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, 0)
    }

    fun bind() {
        GLES20.glBindTexture(GLES20.GL_TEXTURE_2D, textureId)
    }

    fun dispose() {
        if (textureId != 0) {
            GLES20.glDeleteTextures(1, intArrayOf(textureId), 0)
            textureId = 0
        }
    }
}
