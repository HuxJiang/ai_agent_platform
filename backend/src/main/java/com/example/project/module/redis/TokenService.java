package com.example.project.module.redis;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Service
public class TokenService {

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    // 保存refresh token
    public void storeRefreshToken(String username, String refreshToken, long expireSeconds) {
        String key = "refreshToken:" + refreshToken;
        redisTemplate.opsForValue().set(key, username, expireSeconds, TimeUnit.SECONDS);
    }

    // 根据refresh token查询username
    public String getUsernameByRefreshToken(String refreshToken) {
        return redisTemplate.opsForValue().get("refreshToken:" + refreshToken);
    }

    // 删除refresh token
    public void deleteRefreshToken(String refreshToken) {
        redisTemplate.delete("refreshToken:" + refreshToken);
    }
}