package com.example.mausam

import androidx.lifecycle.Lifecycle
import androidx.test.core.app.launchActivity
import com.example.mausam.leak.LeakCanaryUploadService
import com.example.mausam.ui.LeakingActivity
import leakcanary.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import shark.HeapAnalysisSuccess

class LeakingActivityTest {
    @get:Rule
    val rule = DetectLeaksAfterTestSuccess(tag = "EndOfTest")

    private val throwingReporter = NoLeakAssertionFailedError.throwOnApplicationLeaks()

    @Before
    fun setUp() {
        DetectLeaksAssert.update(AndroidDetectLeaksAssert(
            heapAnalysisReporter = { heapAnalysis ->
                // Upload the heap analysis result
                if (heapAnalysis is HeapAnalysisSuccess) {
                    LeakCanaryUploadService().upload(heapAnalysis)
                }
                // Fail the test if there are application leaks
                throwingReporter.reportHeapAnalysis(heapAnalysis)
            }
        ))
    }


    @Test
    fun initiateLeakActivityRendering() {
        launchActivity<LeakingActivity>().use { scenario ->
            scenario.moveToState(Lifecycle.State.CREATED)
        }
        LeakAssertions.assertNoLeaks(tag = "addItemToMausamRendering")
    }
}