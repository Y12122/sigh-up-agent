import { SafetyCertificateOutlined } from "@ant-design/icons";
import { ConfigProvider, Layout, Space, Typography } from "antd";

const { Header, Content } = Layout;

export function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          borderRadius: 6,
          colorPrimary: "#176b5b"
        }
      }}
    >
      <Layout style={{ minHeight: "100vh", background: "#f4f6f5" }}>
        <Header style={{ background: "#fff", borderBottom: "1px solid #e5e7e6" }}>
          <Space>
            <SafetyCertificateOutlined style={{ color: "#176b5b" }} />
            <Typography.Title level={4} style={{ margin: 0 }}>
              工商注册工作台
            </Typography.Title>
          </Space>
        </Header>
        <Content style={{ padding: 24 }} />
      </Layout>
    </ConfigProvider>
  );
}

