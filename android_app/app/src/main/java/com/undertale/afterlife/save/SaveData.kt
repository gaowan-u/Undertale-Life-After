package com.undertale.afterlife.save

data class SaveMetadata(
    val version: String = "0.0.1",
    val createdAt: String? = null,
    val lastPlayed: String? = null,
    val playTime: Double = 0.0
)

data class PlayerData(
    val name: String = "Frisk",
    val level: Int = 1,
    val health: Int = 20,
    val maxHealth: Int = 20,
    val attack: Int = 10,
    val defense: Int = 10,
    val gold: Int = 0,
    val items: List<String> = emptyList(),
    val equipment: Map<String, String> = emptyMap()
)

data class ProgressData(
    val currentChapter: Int = 1,
    val currentScene: String = "falling_ruins",
    val completedChapters: List<Int> = emptyList(),
    val unlockedAreas: List<String> = listOf("falling_ruins"),
    val storyFlags: Map<String, Boolean> = emptyMap(),
    val choices: Map<String, String> = emptyMap()
)

data class PositionData(
    val x: Float = 862f,
    val y: Float = 561f,
    val direction: String = "down"
)

data class SettingsData(
    val musicVolume: Float = 0.7f,
    val sfxVolume: Float = 0.8f,
    val language: String = "zh-CN",
    val controls: String = "keyboard"
)

data class SaveData(
    val metadata: SaveMetadata = SaveMetadata(),
    val player: PlayerData = PlayerData(),
    val progress: ProgressData = ProgressData(),
    val position: PositionData = PositionData(),
    val settings: SettingsData = SettingsData()
)

data class SaveSlotInfo(
    val slotId: Int,
    val playerName: String,
    val level: Int,
    val chapter: Int,
    val playTime: Double,
    val lastPlayed: String?,
    val isEmpty: Boolean = false
)
