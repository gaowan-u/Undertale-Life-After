package com.undertale.afterlife.menu

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import com.undertale.afterlife.render.Texture

class HeartCursor(private val size: Int = 30) {

    val texture: Texture

    init {
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)

        val paint = Paint().apply {
            isAntiAlias = true
            color = GameColors.RED
            style = Paint.Style.FILL
        }

        val path = Path()
        val w = size.toFloat()
        val h = size.toFloat()
        path.moveTo(w / 2f, h)
        path.lineTo(0f, h / 4f)
        path.lineTo(w / 4f, 0f)
        path.lineTo(w / 2f, h / 4f)
        path.lineTo(w * 3f / 4f, 0f)
        path.lineTo(w, h / 4f)
        path.close()

        canvas.drawPath(path, paint)
        texture = Texture()
        texture.loadFromBitmap(bitmap)
        bitmap.recycle()
    }

    companion object {
        fun breathingOffset(timeMs: Long, speed: Float = 0.005f, amplitude: Float = 5f): Float =
            kotlin.math.sin(timeMs * speed) * amplitude
    }
}
