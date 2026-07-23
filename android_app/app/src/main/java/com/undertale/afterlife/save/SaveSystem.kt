package com.undertale.afterlife.save

import android.content.Context
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class SaveSystem(private val context: Context) {

    private val saveDir: File
        get() = File(context.filesDir, "saves").also { it.mkdirs() }

    var currentSaveSlot: Int? = null
    var playerName: String = "Frisk"

    private fun getSaveFile(slotId: Int): File =
        File(saveDir, "save_$slotId.json")

    fun saveExists(slotId: Int): Boolean =
        getSaveFile(slotId).exists()

    private fun readSaveFile(slotId: Int): JSONObject? {
        val file = getSaveFile(slotId)
        if (!file.exists()) return null
        return try {
            JSONObject(file.readText())
        } catch (e: Exception) {
            null
        }
    }

    fun createDefaultSaveData(): SaveData = SaveData(
        player = PlayerData(name = playerName)
    )

    fun createNewSave(slotId: Int, name: String? = null): Boolean {
        if (name != null) playerName = name

        val now = getCurrentTimestamp()
        val save = SaveData(
            metadata = SaveMetadata(
                createdAt = now,
                lastPlayed = now,
                playTime = 0.0
            ),
            player = PlayerData(name = playerName)
        )

        return try {
            val json = saveToJson(save)
            getSaveFile(slotId).writeText(json)
            currentSaveSlot = slotId
            true
        } catch (e: Exception) {
            false
        }
    }

    fun loadSave(slotId: Int): SaveData? {
        val json = readSaveFile(slotId) ?: return null
        return try {
            val save = jsonToSave(json)
            currentSaveSlot = slotId
            playerName = save.player.name
            save
        } catch (e: Exception) {
            null
        }
    }

    fun saveGame(gameState: Map<String, Any>): Boolean {
        val slot = currentSaveSlot ?: return false
        val file = getSaveFile(slot)
        if (!file.exists()) return false

        return try {
            val json = JSONObject(file.readText())

            json.getJSONObject("metadata").put("lastPlayed", getCurrentTimestamp())

            val delta = (gameState["playTime"] as? Number)?.toDouble() ?: 0.0
            if (delta in 0.0..86399.0) {
                val meta = json.getJSONObject("metadata")
                meta.put("playTime", meta.getDouble("playTime") + delta)
            }

            (gameState["playerPosition"] as? Map<*, *>)?.let { pos ->
                val posJson = JSONObject()
                pos.forEach { (k, v) -> posJson.put(k.toString(), v) }
                json.put("position", posJson)
            }

            (gameState["playerStats"] as? Map<*, *>)?.let { stats ->
                val allowedKeys = setOf("level", "health", "maxHealth", "attack", "defense", "gold", "items", "equipment")
                val player = json.getJSONObject("player")
                stats.forEach { (k, v) ->
                    val key = k.toString()
                    if (key in allowedKeys) {
                        player.put(key, v)
                    }
                }
            }

            (gameState["progress"] as? Map<*, *>)?.let { prog ->
                val progressJson = json.getJSONObject("progress")
                prog.forEach { (k, v) ->
                    val key = k.toString()
                    if (progressJson.has(key)) {
                        progressJson.put(key, v)
                    }
                }
            }

            file.writeText(json.toString(2))
            true
        } catch (e: Exception) {
            false
        }
    }

    fun deleteSave(slotId: Int): Boolean {
        val file = getSaveFile(slotId)
        return try {
            if (file.exists()) {
                file.delete()
                if (currentSaveSlot == slotId) {
                    currentSaveSlot = null
                }
                true
            } else false
        } catch (e: Exception) {
            false
        }
    }

    fun getSaveInfo(slotId: Int): SaveSlotInfo? {
        val json = readSaveFile(slotId) ?: return null
        return try {
            val meta = json.getJSONObject("metadata")
            val player = json.getJSONObject("player")
            val progress = json.getJSONObject("progress")
            SaveSlotInfo(
                slotId = slotId,
                playerName = player.getString("name"),
                level = player.getInt("level"),
                chapter = progress.getInt("currentChapter"),
                playTime = meta.getDouble("playTime"),
                lastPlayed = meta.optString("lastPlayed", "").ifEmpty { null }
            )
        } catch (e: Exception) {
            null
        }
    }

    fun listSaves(): List<SaveSlotInfo> =
        (1..3).map { slotId ->
            getSaveInfo(slotId) ?: SaveSlotInfo(
                slotId = slotId,
                playerName = "空存档位",
                level = 0,
                chapter = 0,
                playTime = 0.0,
                lastPlayed = null,
                isEmpty = true
            )
        }

    fun getCurrentTimestamp(): String {
        val fmt = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        return fmt.format(Date())
    }

    private fun saveToJson(save: SaveData): String {
        val json = JSONObject()

        json.put("metadata", JSONObject().apply {
            put("version", save.metadata.version)
            put("createdAt", save.metadata.createdAt ?: JSONObject.NULL)
            put("lastPlayed", save.metadata.lastPlayed ?: JSONObject.NULL)
            put("playTime", save.metadata.playTime)
        })

        json.put("player", JSONObject().apply {
            put("name", save.player.name)
            put("level", save.player.level)
            put("health", save.player.health)
            put("maxHealth", save.player.maxHealth)
            put("attack", save.player.attack)
            put("defense", save.player.defense)
            put("gold", save.player.gold)
            put("items", save.player.items)
            put("equipment", JSONObject(save.player.equipment))
        })

        json.put("progress", JSONObject().apply {
            put("currentChapter", save.progress.currentChapter)
            put("currentScene", save.progress.currentScene)
            put("completedChapters", save.progress.completedChapters)
            put("unlockedAreas", save.progress.unlockedAreas)
            put("storyFlags", JSONObject(save.progress.storyFlags))
            put("choices", JSONObject(save.progress.choices))
        })

        json.put("position", JSONObject().apply {
            put("x", save.position.x.toDouble())
            put("y", save.position.y.toDouble())
            put("direction", save.position.direction)
        })

        json.put("settings", JSONObject().apply {
            put("musicVolume", save.settings.musicVolume.toDouble())
            put("sfxVolume", save.settings.sfxVolume.toDouble())
            put("language", save.settings.language)
            put("controls", save.settings.controls)
        })

        return json.toString(2)
    }

    private fun jsonToSave(json: JSONObject): SaveData {
        val meta = json.getJSONObject("metadata")
        val player = json.getJSONObject("player")
        val progress = json.getJSONObject("progress")
        val position = json.getJSONObject("position")
        val settings = json.getJSONObject("settings")

        fun jsonToMap(obj: JSONObject): Map<String, String> {
            val map = mutableMapOf<String, String>()
            obj.keys().forEach { key -> map[key] = obj.getString(key) }
            return map
        }

        fun jsonToStringMap(obj: JSONObject): Map<String, Boolean> {
            val map = mutableMapOf<String, Boolean>()
            obj.keys().forEach { key -> map[key] = obj.getBoolean(key) }
            return map
        }

        return SaveData(
            metadata = SaveMetadata(
                version = meta.getString("version"),
                createdAt = meta.optString("createdAt", "").ifEmpty { null },
                lastPlayed = meta.optString("lastPlayed", "").ifEmpty { null },
                playTime = meta.getDouble("playTime")
            ),
            player = PlayerData(
                name = player.getString("name"),
                level = player.getInt("level"),
                health = player.getInt("health"),
                maxHealth = player.getInt("maxHealth"),
                attack = player.getInt("attack"),
                defense = player.getInt("defense"),
                gold = player.getInt("gold"),
                items = player.getJSONArray("items").let { arr ->
                    (0 until arr.length()).map { arr.getString(it) }
                },
                equipment = jsonToMap(player.getJSONObject("equipment"))
            ),
            progress = ProgressData(
                currentChapter = progress.getInt("currentChapter"),
                currentScene = progress.getString("currentScene"),
                completedChapters = progress.getJSONArray("completedChapters").let { arr ->
                    (0 until arr.length()).map { arr.getInt(it) }
                },
                unlockedAreas = progress.getJSONArray("unlockedAreas").let { arr ->
                    (0 until arr.length()).map { arr.getString(it) }
                },
                storyFlags = jsonToStringMap(progress.getJSONObject("storyFlags")),
                choices = jsonToMap(progress.getJSONObject("choices"))
            ),
            position = PositionData(
                x = position.getDouble("x").toFloat(),
                y = position.getDouble("y").toFloat(),
                direction = position.getString("direction")
            ),
            settings = SettingsData(
                musicVolume = settings.getDouble("musicVolume").toFloat(),
                sfxVolume = settings.getDouble("sfxVolume").toFloat(),
                language = settings.getString("language"),
                controls = settings.getString("controls")
            )
        )
    }
}
