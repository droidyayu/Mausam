package dependencies

object AndroidTestDependencies {
    val instrumentationRunner by lazy {
        "androidx.test.runner.AndroidJUnitRunner"
    }
    val androidJUnit by lazy {
        "androidx.test.ext:junit:${Versions.androidJUnit}"
    }
    val androidJunitKtx by lazy {
        "androidx.test.ext:junit-ktx:${Versions.androidJUnit}"
    }
    val testRules by lazy {
        "androidx.test:rules:${Versions.testVersion}"
    }
    val testCore by lazy {
        "androidx.test:core-ktx:${Versions.testVersion}"
    }
    val leakCanaryInstrumentation by lazy {
        "com.squareup.leakcanary:leakcanary-android-instrumentation:${Versions.leakcanary}"
    }
    val composeUiTest by lazy {
        "androidx.compose.ui:ui-test-junit4:${Versions.composeTest}"
    }

}