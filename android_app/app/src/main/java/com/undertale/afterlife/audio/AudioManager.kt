package com.undertale.afterlife.audio

import android.content.res.AssetManager
import android.media.MediaPlayer
import java.io.IOException

class AudioManager(private val assetManager: AssetManager) {

    private var bgmPlayer: MediaPlayer? = null
    private var currentBgmPath: String? = null
    private var bgmVolume: Float = 0.7f
    private var pendingBgmPath: String? = null

    fun playBGM(assetPath: String, loop: Boolean = true): Boolean {
        if (currentBgmPath == assetPath && bgmPlayer?.isPlaying == true) return true
        if (pendingBgmPath == assetPath) return true

        stopBGM()

        return try {
            val afd = assetManager.openFd(assetPath)
            val player = MediaPlayer().apply {
                setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
                afd.close()
                isLooping = loop
                setVolume(bgmVolume, bgmVolume)
                setOnPreparedListener { mp ->
                    mp.start()
                    pendingBgmPath = null
                }
                prepareAsync()
            }
            bgmPlayer = player
            currentBgmPath = assetPath
            pendingBgmPath = assetPath
            true
        } catch (e: IOException) {
            false
        }
    }

    fun stopBGM() {
        try {
            bgmPlayer?.stop()
            bgmPlayer?.release()
        } catch (_: Exception) {}
        bgmPlayer = null
        currentBgmPath = null
        pendingBgmPath = null
    }

    fun pauseBGM() {
        bgmPlayer?.pause()
    }

    fun resumeBGM() {
        bgmPlayer?.start()
    }

    fun setBgmVolume(volume: Float) {
        bgmVolume = volume.coerceIn(0f, 1f)
        bgmPlayer?.setVolume(bgmVolume, bgmVolume)
    }

    fun isBgmPlaying(): Boolean = bgmPlayer?.isPlaying == true

    fun dispose() {
        stopBGM()
    }
}
