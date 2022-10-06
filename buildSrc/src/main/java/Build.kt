import dependencies.Versions

object Build {
    val buildTools: String by lazy {
        "com.android.tools.build:gradle:${Versions.buildTools}"
    }
    val kotlinGradlePlugin by lazy {
        "org.jetbrains.kotlin:kotlin-gradle-plugin:${Versions.kotlinGradlePlugin}"
    }
    val hiltAndroidGradlePlugin by lazy {
        "com.google.dagger:hilt-android-gradle-plugin:${Versions.hilt}"
    }
    val navSafeArgsGradlePlugin by lazy {
        "androidx.navigation:navigation-safe-args-gradle-plugin:${Versions.navComponent}"
    }
    val crashlyticsPlugin by lazy {
        "com.google.firebase:firebase-crashlytics-gradle:${Versions.crashlytics}"
    }
    val googleServicesPlugin by lazy {
        "com.google.gms:google-services:${Versions.googleServices}"
    }
}