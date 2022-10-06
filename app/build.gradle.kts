import dependencies.AndroidTestDependencies
import dependencies.AnnotationProcessing
import dependencies.Application
import dependencies.Dependencies
import dependencies.SupportDependencies
import dependencies.TestDependencies
import dependencies.Versions

plugins {
    id(Plugins.androidApplication)
    id(Plugins.kotlinAndroid)
    id(Plugins.kotlinKapt)
    id(Plugins.daggerHilt)
    id(Plugins.kotlinParcelize)
    id(Plugins.googleServices)
    id(Plugins.crashlytics)
}

android {
    compileSdk = Versions.compileSdk

    defaultConfig {
        applicationId = Application.applicationId
        minSdk = Versions.minSdk
        targetSdk = Versions.targetSdk
        versionCode = Application.versionCode
        versionName = Application.versionName

        testInstrumentationRunner = AndroidTestDependencies.instrumentationRunner
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }

    buildFeatures {
        viewBinding = true
    }

    packagingOptions {
        resources.excludes += "DebugProbesKt.bin"
    }

    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = Versions.compose
    }
}

dependencies {
    // Kotlin
    implementation(Dependencies.ktx)
    implementation(Dependencies.kotlinDateTime)

    // Support Libraries
    implementation(SupportDependencies.appCompat)
    implementation(SupportDependencies.material)
    implementation(SupportDependencies.constraintLayout)
    implementation(SupportDependencies.composeUI)

    // Dagger Hilt
    implementation(Dependencies.hiltNavigation)
    implementation(Dependencies.hilt)
    kapt(AnnotationProcessing.daggerHiltCompiler)
    kapt(AnnotationProcessing.hiltCompiler)

    // compose
    implementation(Dependencies.composeUi)
    implementation(Dependencies.composeMaterial)
    implementation(Dependencies.composeToolingPreview)
    implementation(Dependencies.composeActivity)

    // Kotlin Coroutines
    implementation(Dependencies.kotlinCoroutinesCore)
    implementation(Dependencies.kotlinCoroutinesAndroid)

    // Retrofit
    implementation(Dependencies.retrofit)
    implementation(Dependencies.retrofitGson)
    implementation(Dependencies.okhttp)
    implementation(Dependencies.okhttpLogging)

    // UI
    implementation(Dependencies.materialIconsCore)
    implementation(Dependencies.materialIconsExtended)
    implementation(Dependencies.lottie)

    // Timber
    implementation(Dependencies.timber)

    // firebase
    implementation(platform(Dependencies.firebase))
    implementation(Dependencies.firebaseCrashlytics)

    // leak canary
    debugImplementation(Dependencies.leakcanary)

    // Unit Testing
    testImplementation(TestDependencies.jUnit)

    // Instrumentation Testing
    androidTestImplementation(AndroidTestDependencies.androidJUnit)
    androidTestImplementation(AndroidTestDependencies.leakCanaryInstrumentation)
    androidTestImplementation(AndroidTestDependencies.composeUiTest)
    androidTestImplementation(AndroidTestDependencies.testCore)
    androidTestImplementation(AndroidTestDependencies.androidJunitKtx)
    androidTestImplementation(AndroidTestDependencies.testRules)
}