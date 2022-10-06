package com.example.mausam.leak

import shark.LeakTrace

open class LeakException(
    private val leak: LeakTrace,
    private val stackTraceList: MutableList<StackTraceElement>
) : Throwable(leak.signature) {

    init {
        updateStackTrace()
    }

    override fun getLocalizedMessage(): String {
        return leak.toString()
    }

    override fun toString(): String {
        return leak.toSimplePathString()
    }

    private fun updateStackTrace() {
        val stackTrace: List<StackTraceElement> = leak.referencePath.map {
            StackTraceElement(
                it.owningClassName + ":" + it.referenceDisplayName,
                it.owningClassSimpleName,
                it.originObject.toString(),
                0
            )
        }
        setStackTrace(stackTraceList.toTypedArray() + stackTrace.toTypedArray())
    }
}