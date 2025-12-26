const { requireTrimmedString, optionalTrimmedString, parseBooleanFlag } = require('../utils/parsing');
const { ensurePositiveInteger } = require('../utils/validation');
const { ensureMysqlReady } = require('../utils/mysql');
const { fetchAgent, fetchAgentWithOwnership, mapAgentRow } = require('../utils/agentStore');

const ALLOWED_CONNECT_TYPES = new Set(['stream-http', 'sse']);

module.exports = async function agentRoute(fastify, opts = {}) {
  const basePath = typeof opts.routePath === 'string' ? opts.routePath : '/agent';
  const swaggerTags = Array.isArray(opts.swaggerTags) ? opts.swaggerTags : ['agents'];

  fastify.route({
    method: 'POST',
    url: `${basePath}/create`,
    schema: {
      tags: swaggerTags,
      summary: 'Create an agent',
      body: {
        type: 'object',
        required: ['name', 'category', 'userId'],
        properties: {
          name: { type: 'string', minLength: 1, maxLength: 255 },
          description: { type: 'string', nullable: true },
          avatar: { type: 'string', nullable: true, maxLength: 255 },
          category: { type: 'string', minLength: 1, maxLength: 64 },
          url: { type: 'string', nullable: true, maxLength: 255 },
          connectType: { type: 'string', enum: ['stream-http', 'sse'], nullable: true },
          isTested: { type: 'boolean', nullable: true },
          isPublic: { type: 'boolean', nullable: true },
          userId: { type: 'integer', minimum: 1 }
        },
        additionalProperties: false
      },
      response: {
        201: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    agent: {
                      type: 'object',
                      properties: {
                        id: { type: 'integer' },
                        name: { type: 'string' },
                        description: { type: ['string', 'null'] },
                        avatar: { type: ['string', 'null'] },
                        category: { type: 'string' },
                        url: { type: ['string', 'null'] },
                        connectType: { type: 'string' },
                        isTested: { type: 'boolean' },
                        isPublic: { type: 'boolean' },
                        createdAt: { type: ['string', 'null'], format: 'date-time' },
                        updatedAt: { type: ['string', 'null'], format: 'date-time' }
                      }
                    }
                  }
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      const {
        name,
        description,
        avatar,
        category,
        url,
        connectType,
        isTested,
        isPublic,
        userId
      } = request.body || {};

      let normalizedName;
      let normalizedDescription;
      let normalizedAvatar;
      let normalizedCategory;
      let normalizedUrl;
      let normalizedConnectType = 'stream-http';
      let normalizedIsTested = false;
      let normalizedIsPublic = false;
      let normalizedUserId;

      try {
        normalizedName = requireTrimmedString(name, 'name', 255);
        normalizedDescription = optionalTrimmedString(description, 'description', 65535);
        normalizedAvatar = optionalTrimmedString(avatar, 'avatar', 255);
        normalizedCategory = requireTrimmedString(category, 'category', 64);
        normalizedUrl = optionalTrimmedString(url, 'url', 255);

        if (connectType !== undefined && connectType !== null) {
          if (typeof connectType !== 'string') {
            throw new Error('connectType must be a string');
          }

          const trimmedConnectType = connectType.trim();
          const lowered = trimmedConnectType.toLowerCase();

          if (!ALLOWED_CONNECT_TYPES.has(lowered)) {
            throw new Error('connectType must be one of stream-http, sse');
          }

          normalizedConnectType = lowered;
        }

        normalizedIsTested = parseBooleanFlag(isTested, 'isTested', false);
        normalizedIsPublic = parseBooleanFlag(isPublic, 'isPublic', false);
        normalizedUserId = ensurePositiveInteger(userId, 'userId');
      } catch (validationError) {
        const message = validationError instanceof Error ? validationError.message : 'Invalid payload';
        return reply.sendError(message, 400);
      }

      const connection = await fastify.mysql.getConnection();

      try {
        await connection.beginTransaction();

        const [insertResult] = await connection.execute(
          'INSERT INTO agent (name, description, avatar, category, url, connect_type, is_tested, is_public) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
          [
            normalizedName,
            normalizedDescription,
            normalizedAvatar,
            normalizedCategory,
            normalizedUrl,
            normalizedConnectType,
            normalizedIsTested ? 1 : 0,
            normalizedIsPublic ? 1 : 0
          ]
        );

        const agentId = insertResult && typeof insertResult.insertId === 'number' ? insertResult.insertId : null;

        if (!agentId) {
          throw new Error('Failed to obtain created agent id');
        }

        await connection.execute(
          'INSERT INTO user_agent (user_id, agent_id, is_owner) VALUES (?, ?, 1) ON DUPLICATE KEY UPDATE is_owner = 1',
          [normalizedUserId, agentId]
        );

        await connection.commit();

        const agent = await fetchAgent(fastify, agentId);

        if (!agent) {
          return reply.sendError('Failed to load created agent', 500);
        }

        return reply.sendSuccess({ agent }, 201, 'Agent created');
      } catch (error) {
        try {
          await connection.rollback();
        } catch (rollbackError) {
          fastify.log.error({ err: rollbackError }, 'Failed to rollback agent creation transaction');
        }

        fastify.log.error({ err: error }, 'Failed to create agent');

        if (error && error.code === 'ER_NO_REFERENCED_ROW_2') {
          return reply.sendError('User does not exist', 404);
        }

        return reply.sendError('Failed to create agent', 500);
      } finally {
        connection.release();
      }
    }
  });

  fastify.route({
    method: 'DELETE',
    url: `${basePath}/delete`,
    schema: {
      tags: swaggerTags,
      summary: 'Delete an agent',
      querystring: {
        type: 'object',
        required: ['agentId', 'userId'],
        properties: {
          agentId: { type: 'integer', minimum: 1 },
          userId: { type: 'integer', minimum: 1 }
        },
        additionalProperties: false
      },
      response: {
        200: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    agentId: { type: 'integer' }
                  }
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        403: { $ref: 'ResponseBase#' },
        404: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      const { agentId: rawAgentId, userId: rawUserId } = request.query || {};

      let agentId;
      let userId;

      try {
        agentId = ensurePositiveInteger(rawAgentId, 'agentId');
        userId = ensurePositiveInteger(rawUserId, 'userId');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid agentId';
        return reply.sendError(message, 400);
      }

      const { agent, isOwner } = await fetchAgentWithOwnership(fastify, agentId, userId);

      if (!agent) {
        return reply.sendError('Agent not found', 404);
      }

      if (!isOwner) {
        return reply.sendError('User does not own the agent', 403);
      }

      try {
        const result = await fastify.mysql.query('DELETE FROM agent WHERE id = ?', [agentId]);

        const affectedRows = result && typeof result.affectedRows === 'number' ? result.affectedRows : 0;

        if (affectedRows === 0) {
          return reply.sendError('Agent not found', 404);
        }

        return reply.sendSuccess({ agentId }, 200, 'Agent deleted');
      } catch (error) {
        fastify.log.error({ err: error, agentId, userId }, 'Failed to delete agent');

        if (error && error.code === 'ER_ROW_IS_REFERENCED_2') {
          return reply.sendError('Agent is referenced by other records', 409);
        }

        return reply.sendError('Failed to delete agent', 500);
      }
    }
  });

  fastify.route({
    method: 'POST',
    url: `${basePath}/test`,
    schema: {
      tags: swaggerTags,
      summary: 'Mark an agent as tested',
      body: {
        type: 'object',
        required: ['agentId', 'userId'],
        properties: {
          agentId: { type: 'integer', minimum: 1 },
          userId: { type: 'integer', minimum: 1 },
          isTested: { type: 'boolean', nullable: true }
        },
        additionalProperties: false
      },
      response: {
        200: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    agent: {
                      type: 'object',
                      properties: {
                        id: { type: 'integer' },
                        isTested: { type: 'boolean' },
                        updatedAt: { type: ['string', 'null'], format: 'date-time' }
                      }
                    }
                  }
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        403: { $ref: 'ResponseBase#' },
        404: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      const { agentId: rawAgentId, userId: rawUserId, isTested } = request.body || {};

      let agentId;
      let userId;
      let normalizedIsTested = true;

      try {
        agentId = ensurePositiveInteger(rawAgentId, 'agentId');
        userId = ensurePositiveInteger(rawUserId, 'userId');
        normalizedIsTested = parseBooleanFlag(isTested, 'isTested', true);
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid payload';
        return reply.sendError(message, 400);
      }

      const { agent: existingAgent, isOwner } = await fetchAgentWithOwnership(fastify, agentId, userId);

      if (!existingAgent) {
        return reply.sendError('Agent not found', 404);
      }

      if (!isOwner) {
        return reply.sendError('User does not own the agent', 403);
      }

      try {
        const result = await fastify.mysql.query(
          'UPDATE agent SET is_tested = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
          [normalizedIsTested ? 1 : 0, agentId]
        );

        const affectedRows = result && typeof result.affectedRows === 'number' ? result.affectedRows : 0;

        if (affectedRows === 0) {
          return reply.sendError('Agent not found', 404);
        }

        const agent = await fetchAgent(fastify, agentId);

        if (!agent) {
          return reply.sendError('Failed to load agent', 500);
        }

        return reply.sendSuccess({ agent }, 200, normalizedIsTested ? 'Agent marked as tested' : 'Agent marked as not tested');
      } catch (error) {
        fastify.log.error({ err: error, agentId, userId }, 'Failed to update agent testing status');
        return reply.sendError('Failed to update agent testing status', 500);
      }
    }
  });

  fastify.route({
    method: 'POST',
    url: `${basePath}/publish`,
    schema: {
      tags: swaggerTags,
      summary: 'Publish or unpublish an agent',
      body: {
        type: 'object',
        required: ['agentId', 'userId'],
        properties: {
          agentId: { type: 'integer', minimum: 1 },
          userId: { type: 'integer', minimum: 1 },
          isPublic: { type: 'boolean', nullable: true }
        },
        additionalProperties: false
      },
      response: {
        200: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    agent: {
                      type: 'object',
                      properties: {
                        id: { type: 'integer' },
                        isPublic: { type: 'boolean' },
                        updatedAt: { type: ['string', 'null'], format: 'date-time' }
                      }
                    }
                  }
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        403: { $ref: 'ResponseBase#' },
        404: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      const { agentId: rawAgentId, userId: rawUserId, isPublic } = request.body || {};

      let agentId;
      let userId;
      let normalizedIsPublic = true;

      try {
        agentId = ensurePositiveInteger(rawAgentId, 'agentId');
        userId = ensurePositiveInteger(rawUserId, 'userId');
        normalizedIsPublic = parseBooleanFlag(isPublic, 'isPublic', true);
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid payload';
        return reply.sendError(message, 400);
      }

      const { agent: existingAgent, isOwner } = await fetchAgentWithOwnership(fastify, agentId, userId);

      if (!existingAgent) {
        return reply.sendError('Agent not found', 404);
      }

      if (!isOwner) {
        return reply.sendError('User does not own the agent', 403);
      }

      try {
        const result = await fastify.mysql.query(
          'UPDATE agent SET is_public = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
          [normalizedIsPublic ? 1 : 0, agentId]
        );

        const affectedRows = result && typeof result.affectedRows === 'number' ? result.affectedRows : 0;

        if (affectedRows === 0) {
          return reply.sendError('Agent not found', 404);
        }

        const agent = await fetchAgent(fastify, agentId);

        if (!agent) {
          return reply.sendError('Failed to load agent', 500);
        }

        return reply.sendSuccess({ agent }, 200, normalizedIsPublic ? 'Agent published' : 'Agent unpublished');
      } catch (error) {
        fastify.log.error({ err: error, agentId, userId }, 'Failed to update agent visibility');
        return reply.sendError('Failed to update agent visibility', 500);
      }
    }
  });

  // 新增 agent update 接口
  fastify.route({
    method: 'POST',
    url: `${basePath}/update`,
    schema: {
      tags: swaggerTags,
      summary: 'Update an agent',
      body: {
        type: 'object',
        required: ['agentId', 'userId'],
        properties: {
          agentId: { type: 'integer', minimum: 1 },
          userId: { type: 'integer', minimum: 1 },
          name: { type: 'string', minLength: 1, maxLength: 255, nullable: true },
          description: { type: 'string', nullable: true },
          avatar: { type: 'string', nullable: true, maxLength: 255 },
          category: { type: 'string', minLength: 1, maxLength: 64, nullable: true },
          url: { type: 'string', nullable: true, maxLength: 255 },
          connectType: { type: 'string', enum: ['stream-http', 'sse'], nullable: true },
          isTested: { type: 'boolean', nullable: true },
          isPublic: { type: 'boolean', nullable: true }
        },
        additionalProperties: false
      },
      response: {
        200: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    agent: {
                      type: 'object',
                      properties: {
                        id: { type: 'integer' },
                        name: { type: 'string' },
                        description: { type: ['string', 'null'] },
                        avatar: { type: ['string', 'null'] },
                        category: { type: 'string' },
                        url: { type: ['string', 'null'] },
                        connectType: { type: 'string' },
                        isTested: { type: 'boolean' },
                        isPublic: { type: 'boolean' },
                        createdAt: { type: ['string', 'null'], format: 'date-time' },
                        updatedAt: { type: ['string', 'null'], format: 'date-time' }
                      }
                    }
                  }
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        403: { $ref: 'ResponseBase#' },
        404: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      const {
        agentId: rawAgentId,
        userId: rawUserId,
        name,
        description,
        avatar,
        category,
        url,
        connectType,
        isTested,
        isPublic
      } = request.body || {};

      let agentId, userId;
      try {
        agentId = ensurePositiveInteger(rawAgentId, 'agentId');
        userId = ensurePositiveInteger(rawUserId, 'userId');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid payload';
        return reply.sendError(message, 400);
      }

      // 检查 agent 是否存在且 user 是否为 owner
      const { agent: existingAgent, isOwner } = await fetchAgentWithOwnership(fastify, agentId, userId);
      if (!existingAgent) {
        return reply.sendError('Agent not found', 404);
      }
      if (!isOwner) {
        return reply.sendError('User does not own the agent', 403);
      }

      // 构造更新字段
      const fields = [];
      const values = [];
      try {
        if (name !== undefined) {
          fields.push('name = ?');
          values.push(requireTrimmedString(name, 'name', 255));
        }
        if (description !== undefined) {
          fields.push('description = ?');
          values.push(optionalTrimmedString(description, 'description', 65535));
        }
        if (avatar !== undefined) {
          fields.push('avatar = ?');
          values.push(optionalTrimmedString(avatar, 'avatar', 255));
        }
        if (category !== undefined) {
          fields.push('category = ?');
          values.push(requireTrimmedString(category, 'category', 64));
        }
        if (url !== undefined) {
          fields.push('url = ?');
          values.push(optionalTrimmedString(url, 'url', 255));
        }
        if (connectType !== undefined) {
          if (typeof connectType !== 'string') throw new Error('connectType must be a string');
          const trimmedConnectType = connectType.trim();
          const lowered = trimmedConnectType.toLowerCase();
          if (!ALLOWED_CONNECT_TYPES.has(lowered)) throw new Error('connectType must be one of stream-http, sse');
          fields.push('connect_type = ?');
          values.push(lowered);
        }
        if (isTested !== undefined) {
          fields.push('is_tested = ?');
          values.push(parseBooleanFlag(isTested, 'isTested', false) ? 1 : 0);
        }
        if (isPublic !== undefined) {
          fields.push('is_public = ?');
          values.push(parseBooleanFlag(isPublic, 'isPublic', false) ? 1 : 0);
        }
      } catch (validationError) {
        const message = validationError instanceof Error ? validationError.message : 'Invalid payload';
        return reply.sendError(message, 400);
      }

      if (fields.length === 0) {
        return reply.sendError('No fields to update', 400);
      }

      fields.push('updated_at = CURRENT_TIMESTAMP');
      const sql = `UPDATE agent SET ${fields.join(', ')} WHERE id = ?`;
      values.push(agentId);

      try {
        const result = await fastify.mysql.query(sql, values);
        const affectedRows = result && typeof result.affectedRows === 'number' ? result.affectedRows : 0;
        if (affectedRows === 0) {
          return reply.sendError('Agent not found', 404);
        }
        const agent = await fetchAgent(fastify, agentId);
        if (!agent) {
          return reply.sendError('Failed to load updated agent', 500);
        }
        return reply.sendSuccess({ agent }, 200, 'Agent updated');
      } catch (error) {
        fastify.log.error({ err: error, agentId, userId }, 'Failed to update agent');
        return reply.sendError('Failed to update agent', 500);
      }
    }
  });
  fastify.route({
    method: 'POST',
    url: `${basePath}/favorite`,
    schema: {
      tags: swaggerTags,
      summary: 'Favorite an agent',
      body: {
        type: 'object',
        required: ['agentId', 'userId'],
        properties: {
          agentId: { type: 'integer', minimum: 1 },
          userId: { type: 'integer', minimum: 1 },
          note: { type: 'string', nullable: true, maxLength: 255 }
        },
        additionalProperties: false
      },
      response: {
        202: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    relationship: {
                      type: 'object',
                      properties: {
                        agentId: { type: 'integer' },
                        userId: { type: 'integer' },
                        isOwner: { type: 'boolean' }
                      }
                    }
                  }
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        404: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      const { agentId: rawAgentId, userId: rawUserId, note } = request.body || {};

      let agentId;
      let userId;

      try {
        agentId = ensurePositiveInteger(rawAgentId, 'agentId');
        userId = ensurePositiveInteger(rawUserId, 'userId');

        if (note !== undefined && note !== null && typeof note !== 'string') {
          throw new Error('note must be a string when provided');
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid payload';
        return reply.sendError(message, 400);
      }

      try {
        const agent = await fetchAgent(fastify, agentId);

        if (!agent) {
          return reply.sendError('Agent not found', 404);
        }

      const [existing] = await fastify.mysql.query(
        'SELECT COUNT(*) as count FROM user_agent WHERE user_id = ? AND agent_id = ?',
        [userId, agentId]
      );

      if (existing.count === 0) {
        // 记录不存在，插入新记录并增加收藏量
        await fastify.mysql.query(
          'INSERT INTO user_agent (user_id, agent_id, is_owner) VALUES (?, ?, 0)',
          [userId, agentId]
        );
        await fastify.mysql.query(
          'UPDATE agent SET favorite_count = favorite_count + 1 WHERE id = ? AND favorite_count >= 0',
          [agentId]
        );
      } else {
        // 记录已存在，不增加收藏量
        console.log('记录已存在，不增加收藏量');
      }

        return reply.sendSuccess(
          {
            relationship: {
              agentId,
              userId,
              isOwner: false
            }
          },
          202,
          'Agent favorited'
        );
      } catch (error) {
        fastify.log.error({ err: error, agentId, userId }, 'Failed to favorite agent');

        if (error && error.code === 'ER_NO_REFERENCED_ROW_2') {
          return reply.sendError('User not found', 404);
        }

        return reply.sendError('Failed to favorite agent', 500);
      }
    }
  });

  fastify.route({
    method: 'DELETE',
    url: `${basePath}/favorite`,
    schema: {
      tags: swaggerTags,
      summary: 'Unfavorite an agent',
      querystring: {
        type: 'object',
        required: ['agentId', 'userId'],
        properties: {
          agentId: { type: 'integer', minimum: 1 },
          userId: { type: 'integer', minimum: 1 }
        },
        additionalProperties: false
      },
      response: {
        202: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    relationship: {
                      type: 'object',
                      properties: {
                        agentId: { type: 'integer' },
                        userId: { type: 'integer' }
                      }
                    }
                  }
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        404: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      const { agentId: rawAgentId, userId: rawUserId } = request.query || {};

      let agentId;
      let userId;

      try {
        agentId = ensurePositiveInteger(rawAgentId, 'agentId');
        userId = ensurePositiveInteger(rawUserId, 'userId');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid payload';
        return reply.sendError(message, 400);
      }

      try {
        const result = await fastify.mysql.query(
          'DELETE FROM user_agent WHERE user_id = ? AND agent_id = ? AND is_owner = 0',
          [userId, agentId]
        );

        const affectedRows = result && typeof result.affectedRows === 'number' ? result.affectedRows : 0;

        if (affectedRows === 0) {
          return reply.sendError('Favorite relationship not found', 404);
        }
        if (affectedRows === 1)
          await fastify.mysql.query(
            'UPDATE agent SET favorite_count = GREATEST(favorite_count - 1, 0) WHERE id = ?',
            [agentId]
          );

        return reply.sendSuccess(
          {
            relationship: {
              agentId,
              userId
            }
          },
          202,
          'Agent unfavorited'
        );
      } catch (error) {
        fastify.log.error({ err: error, agentId, userId }, 'Failed to unfavorite agent');
        return reply.sendError('Failed to unfavorite agent', 500);
      }
    }
  });

  fastify.route({
    method: 'GET',
    url: `${basePath}/public`,
    schema: {
      tags: swaggerTags,
      summary: 'List all public agents',
      response: {
        200: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    agents: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          id: { type: 'integer' },
                          name: { type: 'string' },
                          description: { type: ['string', 'null'] },
                          avatar: { type: ['string', 'null'] },
                          category: { type: 'string' },
                          url: { type: ['string', 'null'] },
                          connectType: { type: 'string' },
                          isTested: { type: 'boolean' },
                          favoriteCount: { type: 'integer' },
                          createdAt: { type: ['string', 'null'], format: 'date-time' },
                          updatedAt: { type: ['string', 'null'], format: 'date-time' }
                        }
                      }
                    }
                  }
                }
              }
            }
          ]
        },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (_request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      try {
        const rows = await fastify.mysql.query(
          'SELECT id, name, description, avatar, category, url, connect_type, is_tested, is_public, favorite_count, created_at, updated_at FROM agent WHERE is_public = 1 ORDER BY updated_at DESC'
        );

        const agents = Array.isArray(rows) ? rows.map((row) => mapAgentRow(row)) : [];

        return reply.sendSuccess({ agents }, 200);
      } catch (error) {
        fastify.log.error({ err: error }, 'Failed to load public agents');
        return reply.sendError('Failed to load agents', 500);
      }
    }
  });

  fastify.route({
    method: 'GET',
    url: `${basePath}/list`,
    schema: {
      tags: swaggerTags,
      summary: 'List agents owned or favorited by a user',
      querystring: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'integer', minimum: 1 }
        },
        additionalProperties: false
      },
      response: {
        200: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    agents: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          id: { type: 'integer' },
                          name: { type: 'string' },
                          description: { type: ['string', 'null'] },
                          avatar: { type: ['string', 'null'] },
                          category: { type: 'string' },
                          url: { type: ['string', 'null'] },
                          connectType: { type: 'string' },
                          isTested: { type: 'boolean' },
                          isPublic: { type: 'boolean' },
                          createdAt: { type: ['string', 'null'], format: 'date-time' },
                          updatedAt: { type: ['string', 'null'], format: 'date-time' },
                          isOwner: { type: 'boolean' }
                        }
                      }
                    }
                  }
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }

      let userId;

      try {
        userId = ensurePositiveInteger(request.query?.userId, 'userId');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid userId';
        return reply.sendError(message, 400);
      }

      try {
        const rows = await fastify.mysql.query(
          'SELECT a.id, a.name, a.description, a.avatar, a.category, a.url, a.connect_type, a.is_tested, a.is_public, a.created_at, a.updated_at, ua.is_owner FROM user_agent ua INNER JOIN agent a ON a.id = ua.agent_id WHERE ua.user_id = ? ORDER BY ua.is_owner DESC, a.updated_at DESC',
          [userId]
        );

        const agents = Array.isArray(rows)
          ? rows.map((row) => ({
              ...mapAgentRow(row),
              isOwner: Number(row.is_owner) === 1
            }))
          : [];

        return reply.sendSuccess({ agents }, 200);
      } catch (error) {
        fastify.log.error({ err: error, userId }, 'Failed to load user agents');
        return reply.sendError('Failed to load agents', 500);
      }
    }
  });
  // 新增 callagent 端口
  fastify.route({
    method: 'POST',
    url: `${basePath}/call`,
    schema: {
      tags: swaggerTags,
      summary: 'Call an agent',
      body: {
        type: 'object',
        required: ['agentId', 'userId', 'messages'],
        properties: {
          agentId: { type: 'integer', minimum: 1 },
          userId: { type: 'integer', minimum: 1 },
          messages: {
            type: 'array',
            minItems: 1,
            maxItems: 100,
            items: {
              type: 'object',
              required: ['role', 'content'],
              properties: {
                role: { type: 'string', minLength: 1, maxLength: 32 },
                content: { type: 'string', minLength: 1, maxLength: 65535 }
              },
              additionalProperties: false
            }
          }
        },
        additionalProperties: false
      },
      response: {
        200: {
          allOf: [
            { $ref: 'ResponseBase#' },
            {
              type: 'object',
              properties: {
                data: {
                  type: 'object',
                  properties: {
                    messages: {
                      type: 'array',
                      items: {
                        type: 'object',
                        properties: {
                          role: { type: 'string' },
                          content: { type: 'string' },
                          name: { type: 'string' },
                          tool_call_id: { type: 'string' },
                          to: { type: 'string' },
                          tool_calls: { type: 'array' }
                        },
                        additionalProperties: true
                      }
                    }
                  },
                  required: ['messages']
                }
              }
            }
          ]
        },
        400: { $ref: 'ResponseBase#' },
        403: { $ref: 'ResponseBase#' },
        404: { $ref: 'ResponseBase#' },
        502: { $ref: 'ResponseBase#' },
        503: { $ref: 'ResponseBase#' }
      }
    },
    handler: async (request, reply) => {
      // 1. 校验参数
      if (!ensureMysqlReady(fastify, reply)) {
        return;
      }
      const { agentId: rawAgentId, userId: rawUserId, messages } = request.body || {};
      let agentId, userId, normalizedMessages;
      try {
        agentId = ensurePositiveInteger(rawAgentId, 'agentId');
        userId = ensurePositiveInteger(rawUserId, 'userId');
        if (!Array.isArray(messages) || messages.length === 0) {
          throw new Error('messages must be a non-empty array');
        }
        normalizedMessages = messages.map((msg, idx) => {
          if (
            typeof msg !== 'object' ||
            typeof msg.role !== 'string' || !msg.role.trim() || msg.role.length > 32 ||
            typeof msg.content !== 'string' || !msg.content.trim() || msg.content.length > 65535
          ) {
            throw new Error(`Invalid message at index ${idx}`);
          }
          return {
            role: msg.role.trim(),
            content: msg.content.trim()
          };
        });
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Invalid payload';
        return reply.sendError(message, 400);
      }

      // 2. 校验用户与 agent 是否有关联（只要存在表项即可）
      const relationRows = await fastify.mysql.query(
        'SELECT 1 FROM user_agent WHERE user_id = ? AND agent_id = ? LIMIT 1',
        [userId, agentId]
      );
      if (!Array.isArray(relationRows) || relationRows.length === 0) {
        return reply.sendError('User does not own or favorite the agent', 403);
      }

      // 3. 获取 agent 详细信息
      const agentRow = await fastify.mysql.query(
        'SELECT id, url FROM agent WHERE id = ? LIMIT 1',
        [agentId]
      );
      if (!Array.isArray(agentRow) || agentRow.length === 0) {
        return reply.sendError('Agent not found', 404);
      }
      const agent = agentRow[0];

      // 4. 连接 mainagent（url 固定）
      const mainAgentUrl = 'http://localhost:3100/mcp';
      let McpClient;
      try {
        McpClient = require('../mcp/client').McpClient;
      } catch (e) {
        return reply.sendError('McpClient not found', 500);
      }
      const client = new McpClient({ url: mainAgentUrl });
      let toolDefinitions = [];
      let toolMap = new Map();
      let agentTools = [];
      // 5. 获取 agent 可用工具
      try {
        await client.connect();
        // agent.url 作为子 agent，获取工具
        if (agent.url) {
          const subClient = new McpClient({ url: agent.url });
          try {
            await subClient.connect();
            const toolsResult = await subClient.listTools();
            // 打印 agent 工具返回
            fastify.log.info({ agentToolsResult: toolsResult }, '[DEBUG] agent.listTools 返回');
            if (toolsResult && Array.isArray(toolsResult.tools)) {
              agentTools = toolsResult.tools;
            }
          } catch (e) {
            fastify.log.error({ err: e }, '[DEBUG] agent.listTools 异常');
          } finally {
            try { await subClient.disconnect(); } catch (_) {}
          }
        }
        // 构造 tools 供主 agent 调用
        toolDefinitions = Array.isArray(agentTools)
          ? agentTools.map((tool) => {
              const name = typeof tool.name === 'string' ? tool.name.trim() : '';
              return {
                type: 'function',
                function: {
                  name: name,
                  description: tool.description || '',
                  parameters: tool.inputSchema || tool.input_schema || { type: 'object', properties: {}, additionalProperties: true }
                }
              };
            })
          : [];
        toolMap = new Map();
        for (const tool of agentTools) {
          if (tool && tool.name) {
            toolMap.set(tool.name, tool);
          }
        }
      } catch (e) {
        fastify.log.error({ err: e }, '[DEBUG] mainagent/agent工具获取异常');
        try { await client.disconnect(); } catch (_) {}
        return reply.sendError('Failed to connect to main agent', 502);
      }

      // 6. 工具调用主循环
      const MAX_TOOL_ITER = 6;
      let conversationMessages = [...normalizedMessages];
      let finalReply = null;
      try {
        for (let i = 0; i < MAX_TOOL_ITER; i++) {
          const callArguments = {
            messages: conversationMessages,
            tools: toolDefinitions,
            toolChoice: toolDefinitions.length > 0 ? 'auto' : undefined
          };
          // 打印 mainagent 调用参数
          fastify.log.info({ callArguments }, '[DEBUG] mainagent.callTool 入参');
          const toolResult = await client.callTool({ name: 'chat', arguments: callArguments });
          // 打印 mainagent 返回
          fastify.log.info({ toolResult }, '[DEBUG] mainagent.callTool 返回');
          // 解析回复
          let content = '';
          if (Array.isArray(toolResult?.content)) {
            content = toolResult.content
              .filter((part) => part && part.type === 'text' && typeof part.text === 'string')
              .map((part) => part.text)
              .join('');
          } else if (typeof toolResult?.content === 'string') {
            content = toolResult.content;
          }
          // 检查是否有工具调用
          let toolCalls = [];
          const assistantMsg = {
            role: 'assistant',
            content: content || '[empty]'
          };
          if (toolResult?.metadata && Array.isArray(toolResult.metadata.tool_calls)) {
            toolCalls = toolResult.metadata.tool_calls;
          }

          let normalizedToolCalls=[];
          // 每次都将 callTool 返回的 assistant 消息（含 tool_calls）追加到 messages
          if (toolCalls.length > 0) {
            // 仿照 message/send 标准化 tool_calls
            normalizedToolCalls = toolCalls.map((call) => {
              let name = call.name;
              let args = call.arguments;
              // 保证 name/arguments 都为非空字符串，否则丢弃该 tool_call
              if (!name || !args) return null;
              return {
                type: 'function',
                id: typeof call.id === 'string' && call.id.trim().length > 0 ? call.id.trim() : undefined,
                function: {
                  name,
                  arguments: args
                }
              };
            }).filter(Boolean);
            fastify.log.info( '[DEBUG] toolCalls 信息标准化完成');
            if (normalizedToolCalls.length > 0) {
              assistantMsg.tool_calls = normalizedToolCalls;
              fastify.log.info( '[DEBUG] toolCalls 添加到 assistantMsg 完成');
            }
          }
          conversationMessages.push(assistantMsg);
          // 打印每轮后的 conversationMessages
          fastify.log.info({ conversationMessages }, '[DEBUG] conversationMessages (after assistantMsg)');
                    // 打印 toolCalls
          fastify.log.info({ normalizedToolCalls }, '[DEBUG] normalizedToolCalls');
          if (!toolCalls.length) {
            break;
          }
          // 工具调用，依次处理
          for (const call of normalizedToolCalls) {
            const toolName = call.function?.name;
            const toolArgs = call.function?.arguments;
            const toolDef = toolMap.get(toolName);
            let toolResp = '[tool call failed]';
            if (toolDef && typeof toolDef.call === 'function') {
              try {
                // 这里假设工具有 call 方法，实际应根据 agent.url 远程调用
                toolResp = await toolDef.call(toolArgs);
              } catch (e) {
                toolResp = '[tool call error]';
              }
            } else if (agent.url) {
              // 远程调用子 agent 工具
              try {
                const subClient = new McpClient({ url: agent.url });
                await subClient.connect();
                // 打印 agent 工具调用参数
                fastify.log.info({ toolName, toolArgs }, '[DEBUG] agent.callTool 入参');
                toolResp = await subClient.callTool({ name: toolName, arguments: JSON.parse(toolArgs) });
                // 打印 agent 工具调用返回
                fastify.log.info({ toolResp }, '[DEBUG] agent.callTool 返回');
                await subClient.disconnect();
                if (toolResp && typeof toolResp === 'object' && toolResp.content) {
                  toolResp = typeof toolResp.content === 'string' ? toolResp.content : JSON.stringify(toolResp.content);
                } else {
                  toolResp = JSON.stringify(toolResp);
                }
              } catch (e) {
                fastify.log.error({ err: e }, '[DEBUG] agent.callTool 异常');
                toolResp = '[tool call error]';
              }
            }
            // 工具回复消息，必须紧跟在带 tool_calls 的 assistant 消息后
            conversationMessages.push({
              role: 'tool',
              content: toolResp,
              tool_call_id: call.id || undefined,
              to: 'assistant',
              name: toolName
            });
            // 打印每次 tool 回复后的 conversationMessages
            fastify.log.info({ conversationMessages }, '[DEBUG] conversationMessages (after tool reply)');
          }
        }
        await client.disconnect();
        // 只返回最新一条消息
        const latestMessage = conversationMessages.length > 0 ? conversationMessages[conversationMessages.length - 1] : null;
        return reply.sendSuccess(
          { messages: latestMessage ? [latestMessage] : [] },
          200,
          'Agent called successfully'
        );
      } catch (e) {
        fastify.log.error({ err: e }, '[DEBUG] mainagent/agent调用主循环异常');
        try { await client.disconnect(); } catch (_) {}
        return reply.sendError('Failed to call agent', 502);
      }
    }
  });
};
