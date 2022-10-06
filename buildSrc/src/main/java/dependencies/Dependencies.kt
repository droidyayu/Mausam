package dependencies

object Dependencies {

    val ktx by lazy {
        "androidx.core:core-ktx:${Versions.ktx}"
    }
    val kotlinCoroutinesCore by lazy {
        "org.jetbrains.kotlinx:kotlinx-coroutines-core:${Versions.kotlinCoroutines}"
    }
    val kotlinCoroutinesAndroid by lazy {
        "org.jetbrains.kotlinx:kotlinx-coroutines-android:${Versions.kotlinCoroutines}"
    }
    val retrofit by lazy {
        "com.squareup.retrofit2:retrofit:${Versions.retrofit}"
    }
    val retrofitGson by lazy {
        "com.squareup.retrofit2:converter-gson:${Versions.retrofit}"
    }
    val okhttp by lazy {
        "com.squareup.okhttp3:okhttp:${Versions.okhttp}"
    }
    val okhttpLogging by lazy {
        "com.squareup.okhttp3:logging-interceptor:${Versions.okhttp}"
    }
    val materialIconsCore by lazy {
        "androidx.compose.material:material-icons-core:${Versions.materialIcons}"
    }
    val materialIconsExtended by lazy {
        "androidx.compose.material:material-icons-extended:${Versions.materialIcons}"
    }
    val timber by lazy {
        "com.jakewharton.timber:timber:${Versions.timber}"
    }
    val kotlinDateTime by lazy {
        "org.jetbrains.kotlinx:kotlinx-datetime:${Versions.kotlinDateTime}"
    }

    val hilt by lazy {
        "com.google.dagger:hilt-android:${Versions.hilt}"
    }
    val hiltNavigation by lazy {
        "androidx.hilt:hilt-navigation-compose:${Versions.hiltNavigationCompose}"
    }

    val composeUi by lazy {
        "androidx.compose.ui:ui:${Versions.compose}"
    }

    val composeMaterial by lazy {
        "androidx.compose.material:material:${Versions.compose}"
    }
    val composeToolingPreview by lazy {
        "androidx.compose.ui:ui-tooling-preview:${Versions.compose}"
    }
    val composeActivity by lazy {
        "androidx.activity:activity-compose:${Versions.composeActivity}"
    }
    val firebase by lazy {
        "com.google.firebase:firebase-bom:${Versions.firebase}"
    }
    val firebaseCrashlytics by lazy {
        "com.google.firebase:firebase-crashlytics-ktx"
    }
    val lottie by lazy {
        "com.airbnb.android:lottie:${Versions.lottie}"
    }
    val leakcanary by lazy {
        "com.squareup.leakcanary:leakcanary-android:${Versions.leakcanary}"
    }
}