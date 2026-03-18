import NextAuth from 'next-auth'
import type { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import type { User as NextAuthUser } from 'next-auth'

// For MVP, we use a simple credentials provider.
// In production, replace with proper identity provider (Azure AD, Google, etc.)
const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'CyberShield',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        // Demo: accept any credentials matching demo user
        if (
          credentials?.email === 'admin@acmelawfirm.com' &&
          credentials?.password === 'demo'
        ) {
          return {
            id: '00000000-0000-0000-0000-000000000001',
            email: 'admin@acmelawfirm.com',
            name: 'IT Admin',
            tenant_id: '00000000-0000-0000-0000-000000000001',
          }
        }
        return null
      },
    }),
  ],
  session: { strategy: 'jwt' },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.tenant_id = (user as any).tenant_id
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).tenant_id = token.tenant_id
      }
      return session
    },
  },
  pages: {
    signIn: '/login',
  },
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
