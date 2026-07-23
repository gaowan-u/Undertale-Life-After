package com.undertale.afterlife

import android.app.Activity
import android.graphics.BitmapFactory
import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.VideoView
import android.view.View
import android.view.WindowManager
import java.io.File
import java.io.FileOutputStream

class MainActivity : Activity() {

    private lateinit var container: FrameLayout
    private lateinit var gameView: GameView
    private var splashImage: ImageView? = null
    private var videoView: VideoView? = null
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setupImmersive()

        container = FrameLayout(this).apply {
            setBackgroundColor(0xFF000000.toInt())
        }
        setContentView(container)

        showSplashImage()
    }

    private fun showSplashImage() {
        splashImage = ImageView(this).apply {
            try {
                setImageBitmap(BitmapFactory.decodeStream(assets.open("images/background_0.jpg")))
            } catch (_: Exception) {}
            scaleType = ImageView.ScaleType.FIT_CENTER
            setBackgroundColor(0xFF000000.toInt())
        }
        container.addView(splashImage, FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT
        ))

        handler.postDelayed({ showVideo() }, 1500L)
    }

    private fun showVideo() {
        splashImage?.let { container.removeView(it) }
        splashImage = null

        val videoFile = copyVideoToCache()

        val dm = resources.displayMetrics
        val sw = dm.widthPixels
        val sh = dm.heightPixels
        val videoAspect = 1920f / 1080f
        val screenAspect = sw.toFloat() / sh
        val displayW: Int
        val displayH: Int
        if (screenAspect > videoAspect) {
            displayH = sh
            displayW = (sh * videoAspect).toInt()
        } else {
            displayW = sw
            displayH = (sw / videoAspect).toInt()
        }

        val lp = FrameLayout.LayoutParams(displayW, displayH).apply {
            gravity = Gravity.CENTER
        }

        videoView = VideoView(this).apply {
            setVideoURI(Uri.fromFile(videoFile))
            setOnCompletionListener { onVideoComplete() }
            setOnErrorListener { _, _, _ -> onVideoComplete(); true }
            start()
        }
        container.addView(videoView, lp)
    }

    private fun onVideoComplete() {
        handler.post {
            videoView?.let { container.removeView(it) }
            videoView = null

            gameView = GameView(this)
            container.addView(gameView, FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            ))
        }
    }

    private fun copyVideoToCache(): File {
        val file = File(cacheDir, "intro_video.mp4")
        if (!file.exists() || file.length() == 0L) {
            val input = assets.open("videos/begin.mp4")
            val output = FileOutputStream(file)
            input.copyTo(output)
            output.close()
            input.close()
        }
        return file
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) hideSystemUi()
    }

    override fun onResume() {
        super.onResume()
        hideSystemUi()
        if (::gameView.isInitialized) gameView.onResume()
    }

    override fun onPause() {
        super.onPause()
        if (::gameView.isInitialized) gameView.onPause()
    }

    override fun onDestroy() {
        super.onDestroy()
        videoView?.stopPlayback()
    }

    private fun setupImmersive() {
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
    }

    private fun hideSystemUi() {
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            or View.SYSTEM_UI_FLAG_FULLSCREEN
        )
    }
}
