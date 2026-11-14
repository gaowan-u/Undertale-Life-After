package com.undertale.afterlife.game

import android.content.res.AssetManager
import org.json.JSONObject

object MapBoundary {

    private var polygon: List<Pair<Float, Float>>? = null

    fun load(assetManager: AssetManager) {
        if (polygon != null) return
        try {
            val input = assetManager.open("data/map_boundary.json")
            val json = JSONObject(input.bufferedReader().readText())
            input.close()
            val arr = json.getJSONArray("boundary_points")
            polygon = (0 until arr.length()).map { i ->
                val p = arr.getJSONObject(i)
                p.getDouble("x").toFloat() to p.getDouble("y").toFloat()
            }
        } catch (e: Exception) {
            polygon = emptyList()
        }
    }

    fun isPointInside(x: Float, y: Float): Boolean {
        val poly = polygon ?: return false
        var inside = false
        var j = poly.size - 1
        for (i in poly.indices) {
            val (xi, yi) = poly[i]
            val (xj, yj) = poly[j]
            if ((yi > y) != (yj > y) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
                inside = !inside
            }
            j = i
        }
        return inside
    }
}
