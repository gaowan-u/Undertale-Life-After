package com.undertale.afterlife

import android.content.res.AssetManager
import android.view.KeyEvent
import com.undertale.afterlife.audio.AudioManager
import com.undertale.afterlife.game.GameplayScene
import com.undertale.afterlife.game.MapBoundary
import com.undertale.afterlife.input.InputManager
import com.undertale.afterlife.menu.TextRenderer
import com.undertale.afterlife.render.SpriteBatch
import com.undertale.afterlife.save.SaveSystem
import com.undertale.afterlife.scene.DisclaimerScene
import com.undertale.afterlife.scene.MainMenu
import com.undertale.afterlife.scene.SettingsMenu

class GameManager(
    private val assetManager: AssetManager,
    private val inputManager: InputManager,
    private val saveSystem: SaveSystem,
    private val audioManager: AudioManager
) {
    enum class State {
        DISCLAIMER, MAIN_MENU, SETTINGS, GAMEPLAY
    }

    private var state: State = State.DISCLAIMER
    private val textRenderer = TextRenderer(assetManager)

    private val disclaimerScene = DisclaimerScene(textRenderer)
    private val mainMenu = MainMenu(textRenderer)
    private val settingsMenu = SettingsMenu(textRenderer)
    private var gameplayScene: GameplayScene? = null

    private var navUp = false
    private var navDown = false
    private var select = false
    private var back = false
    private var justPressedKeys: MutableSet<Int> = mutableSetOf()
    private var forceSkip = false
    private var menuBgmPlaying = false

    fun update(deltaTime: Float) {
        val keys = inputManager.keysPressed
        navUp = keys.contains(KeyEvent.KEYCODE_DPAD_UP) || keys.contains(KeyEvent.KEYCODE_W)
        navDown = keys.contains(KeyEvent.KEYCODE_DPAD_DOWN) || keys.contains(KeyEvent.KEYCODE_S)
        select = justPressedKeys.contains(KeyEvent.KEYCODE_ENTER) || justPressedKeys.contains(KeyEvent.KEYCODE_SPACE)
        back = justPressedKeys.contains(KeyEvent.KEYCODE_ESCAPE) || justPressedKeys.contains(KeyEvent.KEYCODE_BACK)

        val skipPressed = justPressedKeys.isNotEmpty() && !navUp && !navDown
        val mx = inputManager.mouseLogicalX
        val my = inputManager.mouseLogicalY
        val mouseClicked = inputManager.mouseDown

        when (state) {
            State.DISCLAIMER -> {
                if (disclaimerScene.update(deltaTime, skipPressed || forceSkip)) {
                    switchState(State.MAIN_MENU)
                }
            }

            State.MAIN_MENU -> {
                if (!menuBgmPlaying) {
                    audioManager.playBGM("audios/menu_music.ogg", loop = true)
                    menuBgmPlaying = true
                }
                val result = mainMenu.handleInput(0f, navUp, navDown, select, back, mx, my, mouseClicked)
                when (result) {
                    "start_game" -> startGameplay()
                    "load_game" -> loadGameFromSave()
                    "open_settings" -> switchState(State.SETTINGS)
                    "exit" -> {}
                }
            }

            State.SETTINGS -> {
                val result = settingsMenu.handleInput(navUp, navDown, select, back, mx, my, mouseClicked)
                when (result) {
                    "back" -> switchState(State.MAIN_MENU)
                    "toggle_touch_ui" -> {
                        val current = gameplayScene?.touchUiVisible ?: true
                        settingsMenu.setTouchUiVisible(!current)
                        gameplayScene?.touchUiVisible = !current
                    }
                }
            }

            State.GAMEPLAY -> {
                val gs = gameplayScene ?: return
                val result = gs.update(deltaTime, back)
                when (result) {
                    "back_to_menu" -> switchState(State.MAIN_MENU)
                    "exit" -> switchState(State.MAIN_MENU)
                }
            }
        }

        justPressedKeys.clear()
    }

    private fun switchState(newState: State) {
        state = newState
        forceSkip = false
        if (newState != State.MAIN_MENU) {
            menuBgmPlaying = false
        }
        if (newState == State.GAMEPLAY) {
            audioManager.stopBGM()
        }
    }

    fun onKeyJustPressed(keyCode: Int) {
        justPressedKeys.add(keyCode)
        forceSkip = true
    }

    fun draw(batch: SpriteBatch) {
        when (state) {
            State.DISCLAIMER -> disclaimerScene.draw(batch)
            State.MAIN_MENU -> mainMenu.draw(batch)
            State.SETTINGS -> settingsMenu.draw(batch)
            State.GAMEPLAY -> gameplayScene?.draw(batch)
        }
    }

    private fun startGameplay() {
        MapBoundary.load(assetManager)
        val gs = GameplayScene(assetManager, inputManager, textRenderer, saveSystem)
        saveSystem.createNewSave(1, saveSystem.playerName)
        gameplayScene = gs
        switchState(State.GAMEPLAY)
    }

    private fun loadGameFromSave() {
        val saves = saveSystem.listSaves()
        val firstFilled = saves.firstOrNull { !it.isEmpty }
        if (firstFilled != null) {
            MapBoundary.load(assetManager)
            val save = saveSystem.loadSave(firstFilled.slotId)
            if (save != null) {
                val gs = GameplayScene(assetManager, inputManager, textRenderer, saveSystem)
                gs.loadFromSave(save)
                gs.touchUiVisible = true
                gameplayScene = gs
                switchState(State.GAMEPLAY)
            }
        }
    }

    fun dispose() {
        audioManager.dispose()
        disclaimerScene.dispose()
        mainMenu.dispose()
        settingsMenu.dispose()
        gameplayScene?.dispose()
        textRenderer.dispose()
    }
}
