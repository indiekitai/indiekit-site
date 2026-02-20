# TypeScript Brand 类型：让类型系统帮你抓 Bug

> TypeScript 的结构类型系统很灵活，但有时候太灵活了。Brand 类型是个简单的技巧，能让你区分"看起来一样但意义不同"的类型。

## 问题场景

假设你有两种 ID：

```typescript
function getUser(userId: string) { ... }
function getOrder(orderId: string) { ... }

const userId = "user_123";
const orderId = "order_456";

// TypeScript 不会报错，但这是 bug
getUser(orderId);  // 传错了！
getOrder(userId);  // 又传错了！
```

userId 和 orderId 都是 string，TypeScript 分不清。这种 bug 编译期发现不了，只能运行时暴露。

## Brand 类型解决方案

给类型加个"品牌标记"：

```typescript
type UserId = string & { __brand: "UserId" };
type OrderId = string & { __brand: "OrderId" };

function getUser(userId: UserId) { ... }
function getOrder(orderId: OrderId) { ... }

const userId = "user_123" as UserId;
const orderId = "order_456" as OrderId;

// 现在 TypeScript 会报错！
getUser(orderId);  // ❌ 类型不匹配
getOrder(userId);  // ❌ 类型不匹配

// 正确用法
getUser(userId);   // ✅
getOrder(orderId); // ✅
```

`__brand` 只存在于类型系统，运行时不存在。它是个"善意的谎言"。

## 通用 Brand 工具类型

```typescript
type Brand<T, B extends string> = T & { __brand: B };

// 用法
type UserId = Brand<string, "UserId">;
type OrderId = Brand<string, "OrderId">;
type Positive = Brand<number, "Positive">;
type Email = Brand<string, "Email">;
type Cents = Brand<number, "Cents">;  // 金额用分表示
```

## 创建 Brand 值的三种方式

### 1. as 断言（简单但不安全）

```typescript
const userId = "user_123" as UserId;
```

问题：`"not_a_user_id" as UserId` 也能通过编译。

### 2. 构造函数（推荐）

```typescript
function createUserId(id: string): UserId {
  if (!id.startsWith("user_")) {
    throw new Error("Invalid user ID format");
  }
  return id as UserId;
}

const userId = createUserId("user_123");  // ✅
const bad = createUserId("order_456");     // 运行时报错
```

### 3. 类型守卫

```typescript
function isUserId(id: string): id is UserId {
  return id.startsWith("user_");
}

const input = "user_123";
if (isUserId(input)) {
  getUser(input);  // input 现在是 UserId 类型
}
```

## 实战例子

### 金额处理（避免浮点数问题）

```typescript
type Cents = Brand<number, "Cents">;
type Dollars = Brand<number, "Dollars">;

function toCents(dollars: Dollars): Cents {
  return Math.round(dollars * 100) as Cents;
}

function formatPrice(cents: Cents): string {
  return `$${(cents / 100).toFixed(2)}`;
}

const price = 19.99 as Dollars;
const cents = toCents(price);  // 1999
formatPrice(cents);  // "$19.99"

// 防止直接用裸数字
formatPrice(1999);  // ❌ 类型错误
```

### 已验证 vs 未验证数据

```typescript
type RawInput = Brand<string, "RawInput">;
type SanitizedInput = Brand<string, "Sanitized">;

function sanitize(input: RawInput): SanitizedInput {
  return input.replace(/<[^>]*>/g, "") as SanitizedInput;
}

function insertToDb(data: SanitizedInput) {
  // 安全地插入数据库
}

const userInput = req.body.comment as RawInput;
insertToDb(userInput);  // ❌ 必须先 sanitize

const clean = sanitize(userInput);
insertToDb(clean);  // ✅
```

### 绝对路径 vs 相对路径

```typescript
type AbsolutePath = Brand<string, "AbsolutePath">;
type RelativePath = Brand<string, "RelativePath">;

function toAbsolute(base: AbsolutePath, rel: RelativePath): AbsolutePath {
  return path.join(base, rel) as AbsolutePath;
}

function readFile(path: AbsolutePath) { ... }

const configPath = "./config.json" as RelativePath;
readFile(configPath);  // ❌ 需要绝对路径

const absolute = toAbsolute("/app" as AbsolutePath, configPath);
readFile(absolute);  // ✅
```

## 什么时候用 Brand 类型？

✅ **适合**：
- 同类型但语义不同（UserId vs OrderId）
- 需要强制校验流程（Raw → Sanitized）
- 单位转换场景（Cents vs Dollars）
- API 边界的数据标记

❌ **不适合**：
- 简单项目，过度设计
- 类型已经足够区分的场景
- 团队不熟悉这个模式

## 总结

Brand 类型是个简单但强大的技巧：

1. 零运行时开销（只存在于类型系统）
2. 编译期捕获参数传错的 bug
3. 强制代码走正确的验证流程

记住：`__brand` 是个善意的谎言，用它来让 TypeScript 帮你抓更多 bug。
