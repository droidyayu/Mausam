package com.example.mausam.ui

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Bundle
import android.os.Handler
import androidx.appcompat.app.AppCompatActivity
import com.example.mausam.R
import com.example.mausam.databinding.ActivityLeakingBinding

class LeakingActivity : AppCompatActivity() {
    private var localBroadcastReceiver: BroadcastReceiver? = null
    private val mLeakyHandler: Handler = Handler()

    private var _binding: ActivityLeakingBinding? = null
    private val binding get() = _binding!!

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        _binding = ActivityLeakingBinding.inflate(layoutInflater);
        setContentView(binding.root);
        // Post a message and delay its execution for 10 seconds.
        mLeakyHandler.postDelayed({
            binding.animation.setAnimation(R.raw.done)
            binding.textView.text = "Leaking Done !!"
        }, 1000 * 10)

    }

    private fun registerBroadCastReceiver() {
        localBroadcastReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context, intent: Intent) {
                // Write your code here
            }
        }
        registerReceiver(
            localBroadcastReceiver,
            IntentFilter("android.net.conn.CONNECTIVITY_CHANGE")
        )
    }

    override fun onStart() {
        super.onStart()
        // registering the broadcast receiver
        registerBroadCastReceiver()
    }
}