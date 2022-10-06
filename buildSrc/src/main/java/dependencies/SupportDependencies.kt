package dependencies

object SupportDependencies {
    val appCompat by lazy {
        "androidx.appcompat:appcompat:${Versions.appCompat}"
    }
    val material by lazy {
        "androidx.compose.material:material:${Versions.compose}"
    }
    val constraintLayout by lazy {
        "androidx.constraintlayout:constraintlayout:${Versions.constraintLayout}"
    }
    val composeUI by lazy {
        "androidx.compose.ui:ui:${Versions.compose}"
    }
}