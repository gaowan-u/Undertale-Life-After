package com.undertale.afterlife.menu

import android.content.res.AssetManager
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.Typeface
import com.undertale.afterlife.render.Texture

class TextRenderer(private val assetManager: AssetManager) {

    private val textureCache: MutableMap<String, Texture> = mutableMapOf()

    private val typeface: Typeface by lazy {
        Typeface.createFromAsset(assetManager, "fonts/zpix.ttf")
    }

    fun getTextTexture(text: String, size: Float, color: Int): Texture {
        val key = "$text|$size|$color"
        textureCache[key]?.let { return it }

        val paint = Paint().apply {
            isAntiAlias = true
            typeface = this@TextRenderer.typeface
            textSize = size
            setColor(color)
        }

        val bounds = Rect()
        paint.getTextBounds(text, 0, text.length, bounds)

        val pad = 4
        val bmpW = bounds.width() + pad * 2
        val bmpH = bounds.height() + pad * 2
        if (bmpW <= 0 || bmpH <= 0) {
            val fb = Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
            fb.eraseColor(0)
            val tex = Texture()
            tex.loadFromBitmap(fb)
            textureCache[key] = tex
            return tex
        }

        val bitmap = Bitmap.createBitmap(bmpW, bmpH, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawText(text, pad.toFloat(), (bmpH - bounds.bottom - pad).toFloat(), paint)

        val texture = Texture()
        texture.loadFromBitmap(bitmap)
        bitmap.recycle()

        textureCache[key] = texture
        return texture
    }

    fun getTextDimensions(text: String, size: Float): Pair<Float, Float> {
        val paint = Paint().apply {
            isAntiAlias = true
            typeface = this@TextRenderer.typeface
            textSize = size
        }
        val bounds = Rect()
        paint.getTextBounds(text, 0, text.length, bounds)
        return bounds.width().toFloat() to bounds.height().toFloat()
    }

    fun dispose() {
        textureCache.values.forEach { it.dispose() }
        textureCache.clear()
    }
}
