package com.example.project.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Contact;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import io.swagger.v3.oas.annotations.servers.Server;
import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@OpenAPIDefinition(
        info = @Info(
                title = "Project API",
                version = "v1",
                description = "REST API documentation for the Project service.",
                contact = @Contact(name = "Support Team", email = "support@example.com")
        ),
        servers = {
                @Server(url = "/", description = "Default Server")
        },
        security = {
                @SecurityRequirement(name = "BearerAuth")
        }
)
@SecurityScheme(
        name = "BearerAuth",
        type = SecuritySchemeType.HTTP,
        bearerFormat = "JWT",
        scheme = "bearer"
)
public class OpenApiConfig {

    public static final String BEARER_SECURITY_SCHEME = "BearerAuth";

    @Bean
    public OpenAPI springDocOpenAPI() {
        return new OpenAPI()
                .openapi("3.1.0")
                .components(new Components()
                        .addSecuritySchemes(BEARER_SECURITY_SCHEME, new io.swagger.v3.oas.models.security.SecurityScheme()
                                .type(io.swagger.v3.oas.models.security.SecurityScheme.Type.HTTP)
                                .scheme("bearer")
                                .bearerFormat("JWT")))
                .addSecurityItem(new io.swagger.v3.oas.models.security.SecurityRequirement().addList(BEARER_SECURITY_SCHEME))
                .info(new io.swagger.v3.oas.models.info.Info()
                        .title("Project API")
                        .version("v1")
                        .description("REST API documentation for the Project service.")
                        .license(new License().name("Apache 2.0")));
    }
}
