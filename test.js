// 测试用户注册接口
async function testUserRegister() {
  // const url = 'http://39.102.209.62:8080/api/user/register';

  // const requestBody = {
  //   username: "testuser01",
  //   email: "3877612901@qq.com",
  //   password: "12345678"
  // };
  const url = 'http://39.102.209.62:8080/api/user/login';

  const requestBody = {
    username: "testuser01",
    email: "3877612901@qq.com",
    password: "12345678"
  };
  // const url = 'http://39.102.209.62:8080/api/user/refresh';

  // const requestBody = {
  //   refreshToken: "6hB4X6vX3kKwCI97EFe7UucEOemhStLDob-5DN9xQKj-udqRLEcF2k46tDbSyVAQmJ42nhG3BAo50G94vkf44A"
  // };


  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    // 获取响应状态和信息
    const responseData = await response.json();

    console.log('响应状态:', response.status);
    console.log('响应数据:', responseData);

    if (response.ok) {
      console.log('✅ 注册成功！');
    } else {
      console.log('❌ 注册失败:', responseData.message || responseData.error);
    }

    return responseData;
  } catch (error) {
    console.error('❌ 请求失败:', error);
  }
}

// 执行测试
testUserRegister();